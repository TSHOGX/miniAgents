from typing import Optional
from agent_base import Agent, XResponse, format_agents_response
from prompt import PROMPTS

# from tools import tool_excute_sql, tool_extract_sql_list
# from utils import logger
# from prompts.table_description import table_description, sql_example


class GetDbInfo(Agent):
    """Database information specialist answering general questions about data structure"""

    def work(self, query: str) -> XResponse:
        """Process database information requests"""
        try:
            formatted_query = PROMPTS["get_db_info"].format(
                table_description=table_description, query=query
            )

            response = self.get_response(formatted_query)
            content = self.get_content(response, False)

            logger.info(f"[{self.agent_name}] Processed DB query: {query}")

            return format_agents_response(
                name="DB Info Manager",
                status="success",
                message=content,
                result_path=None,  # Updated to match actual usage
            )

        except Exception as e:
            logger.error(f"[{self.agent_name}] Error processing query: {str(e)}")
            return format_agents_response(
                name="DB Info Manager",
                status="failure",
                message=f"Error processing request: {str(e)}",
                result_path=None,
            )


###


from typing import Optional
from .agent import Agent, XResponse, format_agents_response
from .tools import tool_excute_sql, tool_extract_sql_list
from utils import logger
from prompts.table_description import table_description, sql_example


class GetDbInfo(Agent):
    """Database information specialist answering general questions about data structure"""

    PROMPT_TEMPLATE = """**As a professional data analyst, answer user questions about the database using the following schema:**

## Database Schema
{table_description}

## User Question
{query}

## Requirements
1. Analyze complex questions by extracting key points
2. Select appropriate tables/columns based on schema understanding
3. Provide clear, structured responses using markdown formatting"""

    def work(self, query: str) -> XResponse:
        """Process database information requests"""
        try:
            formatted_query = self.PROMPT_TEMPLATE.format(
                table_description=table_description, query=query
            )

            response = self.get_response(formatted_query)
            content = self.get_content(response, False)

            logger.info(f"[{self.agent_name}] Processed DB query: {query}")

            return format_agents_response(
                name="DB Info Manager",
                status="success",
                message=content,
                result_path=None,  # Updated to match actual usage
            )

        except Exception as e:
            logger.error(f"[{self.agent_name}] Error processing query: {str(e)}")
            return format_agents_response(
                name="DB Info Manager",
                status="failure",
                message=f"Error processing request: {str(e)}",
                result_path=None,
            )


###

from .agent import Agent, format_agents_response
from .tools import tool_excute_sql, tool_extract_sql_list
from utils import *


class GetDbInfo(Agent):
    """根据表格字段说明和其他基础信息, 回答用户一些General的问题"""

    def __init__(
        self,
        agent_name: str,
        model: str,
        api_base: str,
        api_key: str,
        temperature: float,
        system_prompt: str | None,
    ):
        super().__init__(
            agent_name=agent_name,
            model=model,
            api_base=api_base,
            api_key=api_key,
            temperature=temperature,
            system_prompt=system_prompt,
        )

    def work(self, query: str):

        # # get table name

        # generate sql
        from prompts.table_description import table_description, sql_example

        get_db_info_formated_query = f"""**你是专业的数据分析科学家, 我会提供给你数据库的信息, 包括数据表名, 和对应的字段说明. 请回答用户关于这个数据库的问题.**

## 数据库信息

{table_description}

## 用户问题

{query}

## 输出要求
1. 理解用户提问, 对于复杂的提问, 可以先提取关键要点.
2. 理解数据库结构, 选择合适的表格, 然后根据字段说明, 基于理解回答用户问题.
"""

        response = self.get_response(get_db_info_formated_query)
        content = self.get_content(response, False)

        return format_agents_response(
            "DB Info Manager", "success", content, "data/memory/"
        )
