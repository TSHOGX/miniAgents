from typing import Optional, Dict, Any, List, Union
import json

import psycopg2

from app.agents.base import BaseAgent
from app.prompts.agent_prompts import PROMPTS
from app.prompts.db_info import DB_INFO
from app.schema import Message

from app.config import PGSettings, config

# # Supabase client imports (commented out until needed)
# from supabase import create_client, Client


class SupabaseTransactionAgent(BaseAgent):
    """An agent that chats with a Supabase transactions table.

    This agent helps users query and understand transaction data stored in Supabase.
    It translates natural language questions into SQL queries and presents results
    in a user-friendly format.
    """

    name: str = "SupabaseTransactionAgent"
    description: str = "An agent that chats with Supabase transaction data"
    system_prompt: str = """You are a helpful financial assistant who can analyze transaction data.
You have access to a database of financial transactions and can answer questions about spending patterns,
income sources, transaction categories, and other financial insights."""
    next_step_prompt: str = ""

    # Transaction table schema from DB_INFO
    table_schema: List[Dict[str, Any]] = json.loads(
        DB_INFO["TABLE_TRANSACTIONS"]["table_schema"]
    )
    ledger_categories: List[str] = eval(
        DB_INFO["TABLE_TRANSACTIONS"]["ledger_description"]
    )

    # Initialize the PostgreSQL connection
    pg_connection: psycopg2.extensions.connection = psycopg2.connect(
        host=config.pg.host,
        database=config.pg.database,
        port=config.pg.port,
        user=config.pg.user,
        password=config.pg.password,
    )

    # Autocommit mode to avoid transaction blocks
    pg_connection.autocommit = True

    # Create cursor from connection
    pg_client: psycopg2.extensions.cursor = pg_connection.cursor()

    # Execution control
    max_steps: int = 5  # Maximum attempts to generate or fix SQL code
    max_fix_attempts: int = 2

    def step(self) -> str:
        """Execute a single step in the transaction query workflow."""
        # Get the last user query
        last_message = self.memory.get_recent_messages(1)[-1]
        if last_message.role != "user":
            return "No user query found. Please ask a question about your transactions."

        user_query = last_message.content
        if user_query is None:
            user_query = ""

        # Special commands
        if user_query.lower().strip() in [
            "test connection",
            "test_connection",
            "debug connection",
        ]:
            result = self.test_connection()
            self.update_memory("assistant", result)
            return result

        # Generate SQL query based on the user's question
        sql_query = self._generate_sql_query(user_query)
        if not sql_query:
            self.update_memory(
                "assistant", "I failed to generate a SQL query for your question."
            )
            return "I failed to generate a SQL query for your question."

        # Execute the SQL query against Supabase (simulated for now)
        query_result = self._execute_query(sql_query)
        print(f"=== query_result === {query_result}")

        # Format the results into a user-friendly response
        response = self._format_response(user_query, sql_query, query_result)

        # Store the response in memory
        self.update_memory("assistant", response)
        return response

    def _generate_sql_query(self, user_query: str) -> str:
        """Generate SQL query based on the user's question."""
        prompt = PROMPTS["GENERATE_SQL"].format(
            table_schema=json.dumps(self.table_schema, indent=2),
            ledger_categories=json.dumps(self.ledger_categories, indent=2),
            user_query=user_query,
        )

        messages: List[Union[dict, Message]] = [Message.user(prompt)]
        response = self.llm.ask(messages=messages, stream=False, temperature=0.2)

        # Extract SQL code from the response, removing any markdown formatting
        sql_query = response.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query.split("```sql")[1]
        if "```" in sql_query:
            sql_query = sql_query.split("```")[0]

        return sql_query.strip()

    def _execute_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute SQL query against PostgreSQL database.

        Uses autocommit mode to avoid transaction issues and ensures proper error handling.
        """
        try:
            # Create a new cursor for each query to avoid transaction issues
            with self.pg_connection.cursor() as cursor:
                cursor.execute(sql_query)
                try:
                    # Try to fetch results (for SELECT queries)
                    result = cursor.fetchall()
                    # Convert result to JSON-serializable format
                    serialized_result = json.dumps(result, default=str)
                    return {
                        "status": "success",
                        "data": serialized_result,
                        "query": sql_query,
                    }
                except psycopg2.ProgrammingError:
                    # This happens for non-SELECT queries (INSERT, UPDATE, etc.)
                    # These don't return results to fetch
                    return {
                        "status": "success",
                        "data": "[Command executed successfully]",
                        "query": sql_query,
                    }
        except Exception as e:
            # Ensure any transaction is rolled back on error
            self.pg_connection.rollback()
            return {"status": "error", "message": str(e)}

    def _format_response(
        self, user_query: str, sql_query: str, query_result: Dict[str, Any]
    ) -> str:
        """Format query results into a human-readable response."""
        if query_result["status"] == "error":
            return f"I encountered an error with your query: {query_result['message']}"

        # Data is already in serialized JSON string format from _execute_query
        data = query_result.get("data", "[]")

        # Check if it's a command result with no data to return
        if data == "[Command executed successfully]":
            formatted_data = "Command executed successfully. No data was returned."
        else:
            try:
                # Try to parse and format the JSON string
                parsed_data = json.loads(data)

                # For single-value results (like aggregates), format more clearly
                if len(parsed_data) == 1 and len(parsed_data[0]) == 1:
                    formatted_data = f"Result: {parsed_data[0][0]}"
                else:
                    # Format parsed data with indentation for readability
                    formatted_data = json.dumps(parsed_data, indent=2)
            except json.JSONDecodeError:
                # If there's an issue parsing the JSON, use the raw string
                formatted_data = data

        # For analysis queries, use LLM to generate insights
        prompt = PROMPTS["ANALYZE_SQL"].format(
            user_query=user_query,
            sql_query=sql_query,
            formatted_data=formatted_data,
        )

        messages: List[Union[dict, Message]] = [Message.user(prompt)]
        response = self.llm.ask(messages=messages, stream=False, temperature=0.7)

        return response

    def test_connection(self) -> str:
        """Test the database connection and return status information.

        This method can be called to verify the database connection is working
        and to diagnose connection issues.
        """
        try:
            # Test with a simple query to check connection
            with self.pg_connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS test")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    return "Database connection successful. Test query returned: 1"
                else:
                    return f"Connection established but unexpected result: {result}"
        except Exception as e:
            # If connection fails, return error details
            self.pg_connection.rollback()
            return f"Database connection error: {str(e)}"
