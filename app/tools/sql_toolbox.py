from typing import Dict, Any, List, Union
import json
import re

from app.prompts.agent_prompts import PROMPTS
from app.schema import Message
from app.llm import LLM


def extract_sql_from_llm_response(llm_response: str, no_semicolon: bool = False) -> str:
    """
    Extract SQL from LLM response in markdown format
    """
    sql = llm_response
    pattern = r"```sql(.*?)```"
    sql_code_snippets = re.findall(pattern, llm_response, re.DOTALL)

    if len(sql_code_snippets) > 0:
        sql = sql_code_snippets[-1].strip()

    if no_semicolon:
        sql = sql.rstrip(";")

    return sql.strip()


def fix_sql(sql_code: str, error_message: str, llm: LLM) -> str:
    """
    Fix SQL code based on error message.

    Args:
        sql_code: The SQL code that needs to be fixed
        error_message: The error message from the database
        llm: The LLM instance to use for fixing the SQL

    Returns:
        Fixed SQL code
    """
    # Use the existing FIX_SQL prompt from agent_prompts.py
    prompt = PROMPTS["FIX_SQL"].format(
        sql_code=sql_code,
        error_message=error_message,
    )

    # Create a message for the LLM
    messages: List[Union[dict, Message]] = [Message.user(prompt)]

    # Get the LLM response
    response = llm.ask(messages=messages, stream=False, temperature=0.2)
    print(response)

    # Extract SQL code from the response
    fixed_sql = extract_sql_from_llm_response(response)

    return fixed_sql


def get_sql_debugger_tool() -> Dict[str, Any]:
    """
    Get the SQL debugger tool definition for use with LLM.

    Returns:
        A dictionary containing the tool definition
    """
    return {
        "type": "function",
        "function": {
            "name": "fix_sql",
            "description": "Fix SQL code based on error message",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_code": {
                        "type": "string",
                        "description": "The SQL code that needs to be fixed",
                    },
                    "error_message": {
                        "type": "string",
                        "description": "The error message from the database",
                    },
                },
                "required": ["sql_code", "error_message"],
            },
        },
    }
