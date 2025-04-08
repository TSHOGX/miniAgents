from typing import Optional, Dict, Any, List, Union, cast

from app.logger import logger
from app.agents.base import BaseAgent
from app.prompts.agent_prompts import PROMPTS
from app.prompts.db_info import DB_INFO
from app.schema import Message


class DbInfoAgent(BaseAgent):
    """An agent that provides information about a database based on table descriptions."""

    name: str = "DbInfoAgent"
    description: str = (
        "An agent that answers questions about database tables and structures."
    )
    system_prompt: str = """You are a professional data scientist and analyst. I will provide you with database information, 
including table names and field descriptions. Please answer user questions about this database."""
    next_step_prompt: str = ""

    # Table description containing database schema information
    table_description: str = str(DB_INFO["DB_INFO"])

    def step(self) -> str:
        """Execute a single step to answer database questions."""
        # Get the last user query
        last_message = self.memory.get_recent_messages(1)[-1]
        if last_message.role != "user":
            return "No user query found. Please ask a question about the database."
        # last_user_query = last_message.content

        # Get all user queries
        user_queries = self.memory.get_query_list()
        user_queries = "- " + "\n- ".join(user_queries)
        logger.info(f"User queries: \n{user_queries}")

        # Format the query with table information
        formatted_query = PROMPTS["GET_DB_INFO"].format(
            table_description=self.table_description, user_queries=user_queries
        )

        # Generate a response using the LLM
        response = self.llm.ask(
            messages=[Message.user(formatted_query)],
            temperature=0.7,
            stream=False,
        )
        logger.info(f"Response: \n{response}")

        # Store the response in memory
        self.update_memory("assistant", response)

        return response
