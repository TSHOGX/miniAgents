from typing import Dict, Any, List, Union
import json

from app.prompts.agent_prompts import PROMPTS
from app.schema import Message
from app.llm import LLM


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

    # Extract SQL code from the response, removing any markdown formatting
    fixed_sql = response.strip()
    if fixed_sql.startswith("```sql"):
        fixed_sql = fixed_sql.split("```sql")[1]
    if fixed_sql.endswith("```"):
        fixed_sql = fixed_sql.split("```")[0]

    return fixed_sql.strip()


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
