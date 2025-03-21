from typing import Optional, Dict, Any, List, Tuple, Union

from app.agents.base import BaseAgent
from app.prompts.agent_prompts import PROMPTS
from app.prompts.db_info import DB_INFO
from app.schema import Message


class SQLAgent(BaseAgent):
    """An agent that generates SQL code based on user queries.

    This agent follows the workflow:
    1. Get table name for the query
    2. Generate SQL
    3. (Simulate) Execute SQL
    4. Fix SQL if there are errors
    5. Return results
    """

    name: str = "SQLAgent"
    description: str = (
        "An agent that generates SQL code based on natural language queries"
    )
    system_prompt: str = """You are a professional data scientist and SQL expert, specializing in writing precise SQL queries
based on natural language descriptions. You will analyze user requests and create optimized SQL code."""
    next_step_prompt: str = ""

    # Table description containing database schema information
    table_description: Dict[str, str] = DB_INFO["TABLE_DESCRIPTION"]

    # Execution control
    max_steps: int = 5  # Maximum attempts to generate or fix SQL code
    max_fix_attempts: int = 2  # Maximum attempts to fix SQL errors

    def step(self) -> str:
        """Execute a single step in the SQL generation workflow."""
        # Get the last user query
        last_message = self.memory.get_recent_messages(1)[-1]
        if last_message.role != "user":
            return "No user query found. Please ask a question that requires SQL generation."

        user_query = last_message.content
        # Ensure user_query is always a string
        if user_query is None:
            user_query = ""

        # Step 1: Identify the relevant table
        table_name = self._get_table_name(user_query)
        if table_name == "404":
            self.update_memory(
                "assistant", "I couldn't determine which table to use for your query."
            )
            return "I couldn't determine which table to use for your query."

        # Step 2: Generate SQL
        sql_code = self._generate_sql(user_query, table_name)
        if not sql_code:
            self.update_memory(
                "assistant", "I failed to generate SQL code for your query."
            )
            return "I failed to generate SQL code for your query."

        # Step 3: Simulate SQL execution
        execution_result = self._execute_sql(sql_code)

        # Step 4: Fix SQL if there are errors
        fix_attempts = 0
        while (
            execution_result["status"] == "error"
            and fix_attempts < self.max_fix_attempts
        ):
            fix_attempts += 1
            self.update_memory(
                "assistant",
                f"I encountered an error with the SQL: {execution_result['message']}. Attempting to fix (attempt {fix_attempts})...",
            )

            # Generate fixed SQL
            sql_code = self._fix_sql(sql_code, execution_result["message"])
            execution_result = self._execute_sql(sql_code)

        # Step 5: Return results
        if execution_result["status"] == "success":
            response = f"Successfully generated and executed SQL:\n```sql\n{sql_code}\n```\nResults: {execution_result['message']}"
        else:
            response = f"Failed to execute SQL after {fix_attempts} fix attempts. Last error: {execution_result['message']}\nSQL code:\n```sql\n{sql_code}\n```"

        self.update_memory("assistant", response)
        return response

    def _get_table_name(self, query: str) -> str:
        """Determine the appropriate table to use based on the query."""
        prompt = f"""Based on the following table descriptions and user query, determine which table should be used:

Table descriptions:
{self.table_description}

User query: {query}

First, analyze what information the user is looking for.
Then, determine which table contains the necessary fields to answer the query.
Respond with just the table name, nothing else.
"""

        messages: List[Union[dict, Message]] = [Message.user(prompt)]
        response = self.llm.ask(messages=messages, stream=False)

        # Extract table name from response
        table_name = response.strip().lower()

        # Validate table exists
        if table_name in self.table_description:
            return table_name
        else:
            return "404"  # Table not found

    def _generate_sql(self, query: str, table_name: str) -> str:
        """Generate SQL code based on the user query and identified table."""
        prompt = f"""Generate SQL code for the following query using the {table_name} table:

Table description:
{self.table_description[table_name]}

User query: {query}

Requirements:
1. Write a valid SQL query that addresses the user's request
2. Consider performance optimization
3. Include appropriate filtering, grouping, and ordering
4. Format your response as valid SQL code only

Return only the SQL code, no explanations.
"""

        messages: List[Union[dict, Message]] = [Message.user(prompt)]
        response = self.llm.ask(messages=messages, stream=False, temperature=0.2)

        # Extract SQL code from the response, removing any markdown formatting
        sql_code = response.strip()
        if sql_code.startswith("```sql"):
            sql_code = sql_code.split("```sql")[1]
        if sql_code.endswith("```"):
            sql_code = sql_code.split("```")[0]

        return sql_code.strip()

    def _execute_sql(self, sql_code: str) -> Dict[str, Any]:
        """Simulate SQL execution and return results.

        In a real implementation, this would connect to a database.
        For now, we'll simulate success or failure based on SQL syntax.
        """
        # Very simple simulation - in real code, this would actually execute SQL
        if "SELECT" not in sql_code.upper():
            return {"status": "error", "message": "SQL must include a SELECT statement"}

        if "FROM" not in sql_code.upper():
            return {"status": "error", "message": "SQL must include a FROM clause"}

        # Simulate successful execution
        return {"status": "success", "message": "[Simulated successful query results]"}

    def _fix_sql(self, sql_code: str, error_message: str) -> str:
        """Fix SQL code based on error messages."""
        prompt = f"""The following SQL code generated an error:

```sql
{sql_code}
```

Error message: {error_message}

Please fix the SQL code to resolve this error. Only return the corrected SQL code, no explanations.
"""

        messages: List[Union[dict, Message]] = [Message.user(prompt)]
        response = self.llm.ask(messages=messages, stream=False, temperature=0.2)

        # Extract fixed SQL code from the response
        fixed_sql = response.strip()
        if fixed_sql.startswith("```sql"):
            fixed_sql = fixed_sql.split("```sql")[1]
        if fixed_sql.endswith("```"):
            fixed_sql = fixed_sql.split("```")[0]

        return fixed_sql.strip()
