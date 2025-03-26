from typing import Optional, Dict, Any, List, Union
import json

from app.agents.base import BaseAgent
from app.prompts.agent_prompts import PROMPTS
from app.prompts.db_info import DB_INFO
from app.schema import Message
from app.tools.database import db_tool
from app.tools.sql_debugger import fix_sql

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
            result = db_tool.test_connection()
            self.update_memory("assistant", result)
            return result

        # Generate SQL query based on the user's question
        sql_query = self._generate_sql_query(user_query)
        self.memory.add_sql(sql_query)
        if not sql_query:
            self.update_memory(
                "assistant", "I failed to generate a SQL query for your question."
            )
            return "I failed to generate a SQL query for your question."

        # Execute the SQL query against Supabase
        query_result = db_tool.execute_query(sql_query)
        if query_result["status"] == "error":
            # If the query result is an error, we need to try to fix it
            fix_attempts = 0
            while fix_attempts < self.max_fix_attempts:
                sql_query = fix_sql(sql_query, query_result["message"], self.llm)
                query_result = db_tool.execute_query(sql_query)
                print(f"📝 {fix_attempts}: {query_result}")
                if query_result["status"] == "success":
                    self.memory.add_sql(sql_query)
                    break
                fix_attempts += 1
        if query_result["status"] == "success":
            self.memory.add_df(query_result["data"])

        print(f"📝 final: {query_result}")

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
            table_name="transactions",
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

    def _format_response(
        self, user_query: str, sql_query: str, query_result: Dict[str, Any]
    ) -> str:
        """Format query results into a human-readable response."""
        if query_result["status"] == "error":
            return f"I encountered an error with your query: {query_result['message']}"

        # Data is already in serialized JSON string format from _execute_query
        data = query_result.get("data", "[]")

        # For analysis queries, use LLM to generate insights
        prompt = PROMPTS["ANALYZE_SQL"].format(
            user_query=user_query,
            sql_query=sql_query,
            formatted_data=data.head(5).to_string(),
        )

        messages: List[Union[dict, Message]] = [Message.user(prompt)]
        response = self.llm.ask(messages=messages, stream=False, temperature=0.7)

        return response
