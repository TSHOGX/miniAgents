import difflib
import json
from typing import Optional, Dict, Any, List, Tuple, Union

from app.logger import logger
from app.agents.base import BaseAgent
from app.prompts.agent_prompts import PROMPTS
from app.prompts.db_info import DB_INFO
from app.schema import Message
from app.tools.database import db_tool
from app.tools.sql_toolbox import fix_sql, extract_sql_from_llm_response
from app.tools.visualization import make_chart, get_visualization_tool


class SQLAgent(BaseAgent):
    """An agent that generates SQL code based on user queries."""

    name: str = "SQLAgent"
    description: str = (
        "An agent that generates SQL code based on natural language queries"
    )
    system_prompt: str = (
        """You are a helpful assistant that can generate SQL code based on natural language queries and provide insights based on the query results."""
    )
    next_step_prompt: str = ""

    # Table descriptions
    db_info: str = ""  # database level table descriptions
    table_schema: dict = {}  # table level schema
    helper_info: str = ""  # helper information

    # Execution control
    max_steps: int = 5  # Maximum attempts to generate or fix SQL code
    max_fix_attempts: int = 3  # Maximum attempts to fix SQL errors

    def step(self) -> str:
        """Execute a single step in the SQL generation workflow."""
        # Get the last user query
        last_message = self.memory.get_recent_messages(1)[-1]
        if last_message.role != "user":
            return "No user query found. Please ask a question that requires SQL generation."

        # user_query = last_message.content
        # # Ensure user_query is always a string
        # if user_query is None:
        #     user_query = ""

        # Get all user queries
        user_queries = self.memory.get_query_list()
        user_query = "- " + "\n- ".join(user_queries)
        logger.info(f"User queries: \n{user_query}")

        # Identify the relevant table
        table_name = self._get_table_name(user_query)
        if not table_name:
            self.update_memory(
                "assistant", "I couldn't determine which table to use for your query."
            )
            return "I couldn't determine which table to use for your query."
        logger.info(f"Table name: \n{table_name}")

        # Generate SQL
        sql_code = self._generate_sql(user_query, table_name)
        if not sql_code:
            self.update_memory(
                "assistant", "I failed to generate SQL code for your query."
            )
            return "I failed to generate SQL code for your query."

        # Excute SQL and fix SQL if there are errors
        execution_result = db_tool.execute_query(sql_code)
        fix_attempts = 0
        while (
            execution_result["status"] == "error"
            and fix_attempts < self.max_fix_attempts
        ):
            fix_attempts += 1
            sql_code = fix_sql(
                sql_code,
                self.table_schema[table_name],
                execution_result["message"],
                self.llm,
            )
            execution_result = db_tool.execute_query(sql_code)
            logger.info(f"📝 Fix {fix_attempts}: {execution_result}")
        self.memory.add_df(execution_result["data"])
        self.memory.add_sql(execution_result["query"])
        logger.info(f"SQL code: \n{sql_code}")

        # Format the results into a user-friendly response
        response = self._format_response(user_query, execution_result)
        logger.info(f"Response: \n{response}")

        # Try to call visualization tool
        tools = [get_visualization_tool()]
        ask_tool_response = self.llm.ask_tool(
            [
                Message.user(
                    f"Try to call visualization tool to generate a chart based on the following response: \n{response} \n\nThe column names in the data are: \n{', '.join(self.memory.df_data.columns.tolist())}"
                ),
            ],
            tools=tools,
        )
        if ask_tool_response.tool_calls:
            for tool_call in ask_tool_response.tool_calls:
                if tool_call.function.name == "make_chart":
                    try:
                        # Parse tool call arguments
                        args = json.loads(tool_call.function.arguments)
                        data = self.memory.df_data
                        chart_type = args.get("chart_type")
                        title = args.get("title")
                        x_col = args.get("x_col")
                        y_cols = args.get("y_cols")
                        logger.info(f"Chart type: {chart_type}")
                        logger.info(f"Title: {title}")
                        logger.info(f"X column: {x_col}")
                        logger.info(f"Y columns: {y_cols}")
                        # Call tool function
                        tool_response = make_chart(
                            data, chart_type, title, x_col, y_cols
                        )
                        # Format the response
                        final_response = f"{response}\n\n{tool_response}"
                    except Exception as e:
                        logger.error(f"Error making chart: {e}")
                        final_response = f"{response}\n\n**Error making chart**: {e}"
        else:
            final_response = response

        # Store the response in memory
        self.update_memory("assistant", final_response)
        return final_response

    def _get_table_name(self, query: str) -> str:
        """Determine the appropriate table to use based on the query."""
        prompt = PROMPTS["GET_TABLE_NAME"].format(db_info=self.db_info, query=query)
        messages: List[Union[dict, Message]] = [Message.user(prompt)]
        response = self.llm.ask(messages=messages, stream=False)

        # Check if the query is a substring of any table name
        for table_name in self.table_schema.keys():
            if table_name in response:
                return table_name
            elif response in table_name:
                return table_name

        # Use difflib to find the closest match
        matches = difflib.get_close_matches(response, self.table_schema.keys())
        if matches:
            return matches[0]

        return "404"  # Table not found

    def _generate_sql(self, query: str, table_name: str) -> str:
        """Generate SQL code based on the user query and identified table."""
        prompt = PROMPTS["GENERATE_SQL"].format(
            table_name=table_name,
            table_schema=self.table_schema[table_name],
            helper_info=self.helper_info,
            user_query=query,
        )
        messages: List[Union[dict, Message]] = [Message.user(prompt)]
        response = self.llm.ask(messages=messages, stream=False, temperature=0.2)

        # Extract SQL code from the response
        sql_code = extract_sql_from_llm_response(response, no_semicolon=True)

        return sql_code

    def _format_response(self, user_query: str, query_result: Dict[str, Any]) -> str:
        """Format query results into a human-readable response."""
        if query_result["status"] == "error":
            return f"I encountered an error with your query: {query_result['message']}"

        # Get the query results
        data = query_result.get("data", "[]")

        # Use LLM to generate insights
        prompt = PROMPTS["ANALYZE_SQL"].format(
            user_query=user_query,
            formatted_data=data.head(5).to_string(),
        )

        messages: List[Union[dict, Message]] = [Message.user(prompt)]
        response = self.llm.ask(messages=messages, stream=False, temperature=0.7)

        return response
