import json
from typing import List, Dict, Optional, Any
from sqlalchemy import create_engine, inspect, select, MetaData, Table


class SchemaGenerator:
    def __init__(
        self,
        db_url: str,
        schema: Optional[str] = None,
        ignore_tables: Optional[List[str]] = None,
        include_tables: Optional[List[str]] = None,
        sample_rows: int = 3,
    ):
        """
        Initialize the schema generator.

        Args:
            db_url: SQLAlchemy database URL
            schema: Database schema name (if applicable)
            ignore_tables: List of tables to ignore
            include_tables: List of tables to include (if specified, ignore_tables is ignored)
            sample_rows: Number of sample values to extract for each column
        """
        self.engine = create_engine(db_url)
        self.schema = schema
        self.ignore_tables = ignore_tables or []
        self.include_tables = include_tables
        self.sample_rows = sample_rows
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()
        self.table_schemas = {}

        # Get database name from the URL
        self.db_name = db_url.split("/")[-1].split("?")[0]
        if ":" in self.db_name:
            self.db_name = self.db_name.split(":")[-1]

        # Get usable tables
        self.usable_tables = self._get_usable_tables()

    def _get_usable_tables(self) -> List[str]:
        """Get list of tables to process based on include/ignore configuration."""
        # Get all schemas if no specific schema is provided
        schemas = [self.schema] if self.schema else self.inspector.get_schema_names()

        # Filter out system schemas
        schemas = [s for s in schemas if s not in ["information_schema"]]

        all_tables = []
        for schema in schemas:
            try:
                tables = self.inspector.get_table_names(schema=schema)
                # Add schema prefix to table names
                all_tables.extend([f"{schema}.{table}" for table in tables])
            except Exception as e:
                print(f"Error getting tables for schema {schema}: {e}")
                continue

        if self.include_tables:
            return [t for t in all_tables if t in self.include_tables]
        else:
            return [t for t in all_tables if t not in self.ignore_tables]

    def get_column_samples(
        self, table_name: str, column_name: str, max_samples: int = 3
    ) -> List[Any]:
        """Get sample values for a column."""
        try:
            # Handle schema.table_name format
            if "." in table_name:
                schema, table = table_name.split(".")
            else:
                schema = self.schema
                table = table_name

            table_obj = Table(
                table, self.metadata, schema=schema, autoload_with=self.engine
            )
            query = select(table_obj.c[column_name]).distinct().limit(max_samples)

            with self.engine.connect() as connection:
                result = connection.execute(query)
                values = [row[0] for row in result.fetchall() if row[0] is not None]

            return values
        except Exception as e:
            print(f"Error getting samples for {table_name}.{column_name}: {e}")
            return []

    def generate_schema(self) -> str:
        """Generate the schema description."""
        output = []
        output.append(f"[DB_ID] {self.db_name}")
        output.append("[Schema]")

        for table_name in self.usable_tables:
            # Handle schema.table_name format
            if "." in table_name:
                schema, table = table_name.split(".")
            else:
                schema = self.schema
                table = table_name

            # Get table comment if available
            try:
                table_comment = self.inspector.get_table_comment(table, schema)["text"]
                if table_comment:
                    output.append(f"# Table: {table_name}, {table_comment}")
                else:
                    output.append(f"# Table: {table_name}")
            except:
                output.append(f"# Table: {table_name}")

            self.table_schemas[table_name] = []

            output.append("[")

            # Get primary key columns for the table
            pk_columns = set()
            try:
                pk_info = self.inspector.get_pk_constraint(table, schema)
                pk_columns = set(pk_info.get("constrained_columns", []))
            except:
                pass

            # Process each column
            columns = self.inspector.get_columns(table, schema=schema)
            column_lines = []

            for column in columns:
                column_name = column["name"]
                column_type = f"{column['type']}".upper()

                # Get column description/comment if available
                column_comment = column.get("comment", "")
                if not column_comment:
                    if column_name in pk_columns:
                        column_comment = f"the primary key of {table_name}"
                    else:
                        column_comment = f"the {column_name} of {table_name}"

                # Get sample values
                examples = self.get_column_samples(
                    table_name, column_name, self.sample_rows
                )

                # Format the column line
                column_line = f"({column_name}: {column_type}, {column_comment}"

                if column_name in pk_columns:
                    column_line += ", Primary Key"

                if examples:
                    # Format examples appropriately
                    example_str = ", ".join([str(ex) for ex in examples])
                    column_line += f", Examples: [{example_str}]"

                column_line += ")"
                column_lines.append(column_line)

            output.append(",\n".join(column_lines))
            output.append("]")

        return "\n".join(output)

    def save_schema(self, output_path: str):
        """Save the schema to a file."""
        schema_str = self.generate_schema()
        with open(output_path, "w") as f:
            f.write(schema_str)
        print(f"Schema saved to {output_path}")

    def parse_schema(self, schema_file: str, output_file: str):
        """Parse the schema from a file."""
        table_schemas = {}

        with open(schema_file, "r") as f:
            schema = f.read()

            # read line by line
            lines = schema.split("\n")
            for line in lines:
                if line.startswith("# Table:"):
                    table_name = line.split(":")[1].strip()
                    table_schemas[table_name] = []
                elif line.startswith("["):
                    flag = True
                    continue
                elif line.startswith("]"):
                    flag = False
                    continue
                elif flag:
                    table_schemas[table_name].append(line)

        # save to table_schemas.json (utf-8)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(table_schemas, f, ensure_ascii=False)

        print(f"Schema parsed and saved to {output_file}")
