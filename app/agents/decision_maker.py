from typing import List, Optional

from pydantic import Field

from app.agents.base import BaseAgent
from app.schema import Message, Memory
from app.prompts.agent_prompts import PROMPTS


class DecisionMaker(BaseAgent):
    """Decision maker agent that assigns tasks to appropriate workers.

    This agent examines user queries, summarizes them when needed, and routes
    tasks to the appropriate worker agent based on the query content.
    """

    name: str = "DecisionMaker"
    description: str = (
        "An agent that takes queries and assigns them to appropriate worker agents."
    )
    system_prompt: str = """You are a highly efficient decision maker. 
Your job is to analyze user queries and determine which specialized worker should handle them.
Make decisions based on the nature of the request and the capabilities of available workers."""
    next_step_prompt: str = "What type of worker should handle this query?"

    # Available workers and their descriptions
    workers: List[dict] = Field(
        default=[
            {
                "name": "get_sql",
                "description": "Generate SQL code based on user's input.",
            },
            {
                "name": "get_db_info",
                "description": "Get database information based on user's input.",
            },
            {
                "name": "base_chat",
                "description": "Chat with user based on user's input.",
            },
        ]
    )

    def summarize_queries(self, query: str) -> str:
        """Summarize a list of queries into a single concise query.

        IDEAS:
        - 每一个新存入的query，都提取关键修改点; 然后返回一个包含所有修改点的query
        - 直接返回一个包含所有query的合并query
        - 返回一个 summarized query
        """
        mode = "merge"

        # Get all user queries from memory
        query_list = [
            msg.content
            for msg in self.memory.messages
            if msg.role == "user" and msg.content
        ]

        if mode == "merge":
            final_query = "\n".join(query_list)

        elif mode == "summarize":
            # If only one query, no need to summarize
            if len(query_list) <= 1:
                return query

            # Create prompt for summarizing queries
            prompt = PROMPTS["SUMMARIZE_QUERIES"].format(query_list=query_list)

            # Get response from LLM
            final_query = self.llm.ask(
                messages=[Message.user(prompt)],
                stream=False,
            )

        return final_query

    def assign_worker(self, query: str) -> str:
        """Assign the query to the appropriate worker."""
        worker_names = [worker["name"] for worker in self.workers]

        # Create prompt for worker assignment
        prompt = PROMPTS["ASSIGN_WORKER"].format(
            worker_names=worker_names, workers=self.workers, query=query
        )

        # Get response from LLM
        assigned_worker = self.llm.ask(
            messages=[Message.user(prompt)],
            stream=False,
        )

        return assigned_worker

    def step(self) -> str:
        """Process the user query and assign to appropriate worker."""
        # Get the last message from memory (user query)
        last_message = self.memory.messages[-1] if self.memory.messages else None

        if not last_message or last_message.role != "user" or not last_message.content:
            return "No valid query to process."

        # Get and summarize the query
        user_query = last_message.content
        summarized_query = self.summarize_queries(user_query)

        # Assign to a worker
        assigned_worker = self.assign_worker(summarized_query)

        # Process based on assigned worker
        response = ""

        if "get_sql" in assigned_worker:
            # This would normally create and use the SQLGenerator agent
            # For now, we'll simulate the response
            response = f"""我把任务分配给了 SQL Generator, 他顺利的完成了任务."""

        elif "get_db_info" in assigned_worker:
            # This would normally create and use the GetDbInfo agent
            response = f"""我把任务分配给了 DB Info Manager, 他顺利的完成了任务."""

        else:
            # Default to base chat for general queries
            chat_response = self.llm.ask(
                messages=[Message.user(summarized_query)],
                stream=False,
            )
            response = chat_response

        # Store the response in memory
        self.update_memory("assistant", response)

        return response
