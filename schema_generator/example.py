import os
from schema_generator import SchemaGenerator

if __name__ == "__main__":

    db_url = f"db_name:///db_user:db_pass@db_host:db_port/db_name"
    generator = SchemaGenerator(
        db_url=db_url,
        # schema="public",  # Optional: schema name
        # include_tables=["users", "logs"],  # Optional: only include specific tables
    )
    schema = generator.generate_schema()
    generator.save_schema("schema_generator/schema.txt")

    # parse schema
    generator.parse_schema(
        "schema_generator/schema.txt", "schema_generator/table_schemas.json"
    )
