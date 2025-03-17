from typing import Dict, List, Optional, Any, Tuple
import json
from abc import ABC, abstractmethod

from agent.agent_base import Agent, XResponse, format_agents_response
from llm.llm_base import LLMBase

# Assuming these tools exist or will be implemented
from tools import tool_execute_sql


class NL2SQLAgent(Agent):
    """
    Agent that transforms natural language questions into SQL queries for Clickhouse,
    executes them, and returns results or error information.

    Workflow:
    1. Choose relevant database table based on user query
    2. Write SQL using the table schema
    3. Validate SQL for correctness (field names, Clickhouse functions)
    4. Execute SQL and return results or error information
    5. Handle user feedback for corrections
    """

    def __init__(
        self,
        agent_name: str,
        llm_model: LLMBase,
        table_schemas: Dict[str, Dict],
        prompts: Dict[str, str],
    ):
        """
        Initialize the NL2SQL agent.

        Args:
            agent_name: Identifier for the agent
            llm_model: LLM model for processing
            table_schemas: Database schema information {db_name: {table_name: {schema}}}
            prompts: Dictionary of prompts for different workflow stages
        """
        super().__init__(agent_name=agent_name, llm_model=llm_model)
        self.table_schemas = table_schemas
        self.prompts = prompts

    def work(self, query: str, feedback: Optional[str] = None) -> XResponse:
        """
        Process a natural language query and convert it to SQL.

        Args:
            query: User's natural language question
            feedback: Optional user feedback for SQL refinement

        Returns:
            XResponse with SQL code and results or error information
        """
        try:
            # Step 1: Choose relevant tables
            relevant_tables = self._choose_tables(query)
            if not relevant_tables:
                return format_agents_response(
                    name=self.agent_name,
                    status="failure",
                    message="Could not identify relevant tables for this query.",
                )

            # Step 2: Write SQL based on schema and query
            sql_code = self._write_sql(query, relevant_tables, feedback)
            if not sql_code:
                return format_agents_response(
                    name=self.agent_name,
                    status="failure",
                    message="Failed to generate SQL query.",
                )

            # Step 3: Validate SQL
            validation_result, validation_message = self._validate_sql(
                sql_code, relevant_tables
            )
            if not validation_result:
                return format_agents_response(
                    name=self.agent_name,
                    status="failure",
                    message=f"SQL validation failed: {validation_message}",
                    result_path=json.dumps({"sql_code": sql_code}),
                )

            # Step 4: Execute SQL
            execution_result = tool_execute_sql(sql_code)

            # Step 5: Handle results
            if execution_result == "success":
                return format_agents_response(
                    name=self.agent_name,
                    status="success",
                    message="Query executed successfully.",
                    result_path=json.dumps(
                        {"sql_code": sql_code, "data_path": "data/memory/df.parquet"}
                    ),
                )
            else:
                return format_agents_response(
                    name=self.agent_name,
                    status="failure",
                    message=f"Query execution failed: {execution_result}",
                    result_path=json.dumps({"sql_code": sql_code}),
                )

        except Exception as e:
            return format_agents_response(
                name=self.agent_name,
                status="failure",
                message=f"Error processing query: {str(e)}",
            )

    def _choose_tables(self, query: str) -> List[Tuple[str, str]]:
        """
        Identify relevant database tables for the query.

        Args:
            query: User's natural language question

        Returns:
            List of (database_name, table_name) tuples
        """
        # Construct prompt using the table schema information
        prompt = self.prompts.get("choose_table", "")

        # Format with available schemas
        schema_descriptions = []
        for db_name, tables in self.table_schemas.items():
            for table_name, schema in tables.items():
                schema_str = json.dumps(schema, indent=2)
                schema_descriptions.append(
                    f"Database: {db_name}\nTable: {table_name}\nSchema: {schema_str}"
                )

        formatted_prompt = prompt.format(
            table_schemas="\n\n".join(schema_descriptions), query=query
        )

        # Get response from LLM
        response = self.llm_model.get_response(formatted_prompt)

        # Parse response to get db and table names
        # Format expected: [("db1", "table1"), ("db1", "table2")]
        try:
            # Simple parsing assuming the LLM returns a list of db.table pairs
            relevant_tables = []
            lines = response.strip().split("\n")
            for line in lines:
                if "." in line:
                    parts = line.strip().split(".")
                    if len(parts) == 2:
                        db_name, table_name = parts[0].strip(), parts[1].strip()
                        # Validate that this table exists in our schema
                        if (
                            db_name in self.table_schemas
                            and table_name in self.table_schemas[db_name]
                        ):
                            relevant_tables.append((db_name, table_name))

            return relevant_tables
        except Exception as e:
            print(f"Error parsing tables: {str(e)}")
            return []

    def _write_sql(
        self,
        query: str,
        relevant_tables: List[Tuple[str, str]],
        feedback: Optional[str] = None,
    ) -> str:
        """
        Generate SQL code for the given query and tables.

        Args:
            query: User's natural language question
            relevant_tables: List of (database_name, table_name) tuples
            feedback: Optional user feedback for refinement

        Returns:
            SQL code string
        """
        # Prepare schema information for the relevant tables
        schema_info = []
        for db_name, table_name in relevant_tables:
            schema = self.table_schemas.get(db_name, {}).get(table_name, {})
            schema_str = json.dumps(schema, indent=2)
            schema_info.append(
                f"Database: {db_name}\nTable: {table_name}\nSchema: {schema_str}"
            )

        # Format prompt with schema and query
        prompt = self.prompts.get("write_sql", "")
        formatted_prompt = prompt.format(
            table_schemas="\n\n".join(schema_info),
            query=query,
            feedback=feedback if feedback else "No feedback provided.",
        )

        # Get response from LLM
        response = self.llm_model.get_response(formatted_prompt)

        # Extract SQL code from response
        sql_code = ""
        if "```sql" in response.lower() and "```" in response:
            start = response.lower().find("```sql") + 6
            end = response.find("```", start)
            if start > 6 and end > start:
                sql_code = response[start:end].strip()
        else:
            # Fallback if no code block is found
            sql_code = response.strip()

        return sql_code

    def _validate_sql(
        self, sql_code: str, relevant_tables: List[Tuple[str, str]]
    ) -> Tuple[bool, str]:
        """
        Validate SQL for correctness against schema and Clickhouse requirements.

        Args:
            sql_code: Generated SQL code
            relevant_tables: List of (database_name, table_name) tuples

        Returns:
            Tuple of (is_valid, message)
        """
        # Prepare schema information for the relevant tables
        schema_info = []
        for db_name, table_name in relevant_tables:
            schema = self.table_schemas.get(db_name, {}).get(table_name, {})
            schema_str = json.dumps(schema, indent=2)
            schema_info.append(
                f"Database: {db_name}\nTable: {table_name}\nSchema: {schema_str}"
            )

        # Format prompt with schema and SQL code
        prompt = self.prompts.get("check_sql", "")
        formatted_prompt = prompt.format(
            table_schemas="\n\n".join(schema_info), sql_code=sql_code
        )

        # Get response from LLM
        response = self.llm_model.get_response(formatted_prompt)

        # Parse validation result
        if "valid" in response.lower() and "invalid" not in response.lower():
            return True, "SQL validation passed."
        else:
            # Extract validation message if present
            message = response
            if "reason:" in response.lower():
                message = response.lower().split("reason:")[1].strip()
            return False, message
