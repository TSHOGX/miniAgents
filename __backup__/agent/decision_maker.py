from typing import Optional, Dict, Any
from agent_base import Agent, XResponse, format_agents_response
from utils import mem_sql_code, mem_query
from prompts.agents_info import agents_info
from prompt import PROMPTS

# Central registry of available workers
WORKER_HANDLERS = {
    "get_sql": {
        "agent_key": "SQL Generator",
        "module": "get_sql",
        "class": "SQLGenerator",
        "result_processor": lambda: f"\n```sql\n{mem_sql_code.get_code()}\n```",
    },
    "modify_sql": {
        "agent_key": "SQL Modifier",
        "module": "modify_sql",
        "class": "SQLModifier",
    },
    "get_db_info": {
        "agent_key": "DB Info Manager",
        "module": "get_db_info",
        "class": "GetDbInfo",
    },
    "base_chat": {
        "agent_key": "Base Chatter",
        "module": "base_chatter",
        "class": "BaseChatter",
    },
}


class DecisionMaker(Agent):
    """Orchestrates tasks between different specialized agents based on user queries."""

    def work(self, query: str) -> str:
        """Main workflow processing user queries."""
        mem_query.add(query)
        summarized_query = self._process_query_summary()
        worker_choice = self._determine_worker(summarized_query)
        return self._handle_worker_response(worker_choice, summarized_query)

    def _process_query_summary(self) -> str:
        """Process and summarize query history."""
        # TODO 需要优化 prompt, 可以按点列举所有需求, 而不是 summary
        query_list = mem_query.get_curr_task()
        prompt = PROMPTS["decision_maker_summary"].format(query_list=query_list)
        return self.llm_model.get_response(prompt)

    def _determine_worker(self, query: str) -> str:
        """Determine appropriate worker for the query."""
        # TODO 引入 MCP 来选择最合适的 worker?
        worker_list = [
            {"name": name, "description": config["agent_key"]}
            for name, config in WORKER_HANDLERS.items()
        ]

        prompt = PROMPTS["decision_maker_worker"].format(
            worker_names=list(WORKER_HANDLERS.keys()),
            worker_list=worker_list,
            query=query,
        )
        return self.llm_model.get_response(prompt).strip().lower()

    def _handle_worker_response(self, worker_choice: str, query: str) -> str:
        """Handle the selected worker's response."""
        if worker_choice not in WORKER_HANDLERS:
            return self._handle_fallback(query)

        config = WORKER_HANDLERS[worker_choice]
        agent_info = agents_info[config["agent_key"]]
        agent = self._init_agent(config["module"], config["class"], agent_info)
        xresp = agent.work(query)

        return self._format_response(worker_choice, xresp, config)

    def _init_agent(
        self, module: str, class_name: str, agent_info: Dict[str, Any]
    ) -> Agent:
        """Dynamically initialize the target agent."""
        module = __import__(f".{module}", fromlist=[class_name])
        agent_class = getattr(module, class_name)
        return agent_class(**agent_info)

    def _format_response(
        self, worker_name: str, xresp: XResponse, config: Dict[str, Any]
    ) -> str:
        """Format the final response message."""
        status_msg = (
            "顺利的完成了任务"
            if xresp["status"] == "success"
            else "暂时没法自主完成任务, 需要您的帮助"
        )
        base_msg = f"我把任务分配给了 {xresp['name']}, 他{status_msg}.\n\n[{xresp['name']}] {xresp['content']['message']}"

        if "result_processor" in config:
            return f"{base_msg}\n\n当前结果如下:{config['result_processor']()}"
        return f"{base_msg}\n\n当前结果如下:\n{xresp['content']['message']}"

    def _handle_fallback(self, query: str) -> str:
        """Fallback for unhandled worker choices."""
        return self.llm_model.get_response(query)
