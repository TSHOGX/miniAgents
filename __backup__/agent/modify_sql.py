from agents.agent import Agent, Role, XResponse, format_agents_response
from agents.tools import tool_excute_sql, tool_extract_sql_list
from utils import *


class SQLModifier(Agent):

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

    def work(
        self, sql_code: str, instruction: str, max_try_count: int = 5
    ) -> XResponse:
        """(modify sql -- run/fix code) * n -- response"""
        try_count = 0
        while max_try_count > try_count:
            sql_modifier_query = f"""Please modify the SQL code based on my instruction. Notice that the instruction can be a suggestion or a requirement provided by user, or a error info generated automatically.

SQL platform: ClickHouse

Instruction: {instruction}

Code:
```sql
{sql_code}
```

Modified Code:
"""

            logger.info(f"SQL Modifier round {try_count}.")

            response = self.get_response(sql_modifier_query)
            content = self.get_content(response, False)

            # Extract the modified code
            modified_code = max(tool_extract_sql_list(content), key=len)
            mem_sql_code.set_code(modified_code)

            # Run code
            resp = tool_excute_sql(modified_code)

            # If success, return success
            if resp == "success":
                return format_agents_response(
                    "SQL Modifier",
                    "success",
                    f"Modify Round {try_count}: Success!",
                    None,
                )

            # If failed, try again
            print(resp)
            sql_code = mem_sql_code.get_code()
            instruction = resp

            try_count += 1

        return format_agents_response(
            "SQL Modifier",
            "fail",
            f"Modify Round {try_count}: Run out of count... Sorry I can not solve this problem.",
            None,
        )


####

from typing import Optional
from agents.agent import Agent, XResponse, format_agents_response
from agents.tools import tool_excute_sql, tool_extract_sql_list
from utils import logger, mem_sql_code


class SQLModifier(Agent):
    """SQL code modification specialist handling iterative improvements and error recovery"""

    _SQL_PLATFORM = "ClickHouse"
    _MAX_ATTEMPTS = 5
    _AGENT_NAME = "SQL Modifier"

    _PROMPT_TEMPLATE = """Please modify the SQL code based on the following instruction:
Platform: {platform}
Instruction: {instruction}

Original Code:
```sql
{code}
Modified Code:"""


def work(
    self, sql_code: str, instruction: str, max_try_count: int = _MAX_ATTEMPTS
) -> XResponse:
    """Iteratively modify SQL code based on instructions/errors"""
    current_code = sql_code
    current_instruction = instruction

    for attempt in range(max_try_count):
        logger.info(f"{self._AGENT_NAME} attempt {attempt + 1}/{max_try_count}")

        modified_code = self._modify_sql(current_code, current_instruction)
        if not modified_code:
            return self._failure_response(attempt, "No valid SQL generated")

        execution_result = self._execute_and_validate(modified_code)
        if execution_result.success:
            return self._success_response(attempt, modified_code)

        current_code = modified_code
        current_instruction = execution_result.message

    return self._failure_response(max_try_count, "Max attempts exhausted")


def _modify_sql(self, code: str, instruction: str) -> Optional[str]:
    """Generate modified SQL code with validation"""
    try:
        prompt = self._PROMPT_TEMPLATE.format(
            platform=self._SQL_PLATFORM, instruction=instruction, code=code
        )

        response = self.get_response(prompt)
        content = self.get_content(response, False)

        if sql_candidates := tool_extract_sql_list(content):
            return max(sql_candidates, key=len)

        logger.error("No SQL found in response")
        return None

    except Exception as e:
        logger.error(f"Modification failed: {str(e)}")
        return None


def _execute_and_validate(self, code: str) -> "ExecutionResult":
    """Execute SQL and handle results"""
    try:
        mem_sql_code.set_code(code)
        result = tool_excute_sql(code)
        return ExecutionResult(result == "success", result)
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        return ExecutionResult(False, str(e))


def _success_response(self, attempt: int, code: str) -> XResponse:
    logger.info(f"Success after {attempt + 1} attempts")
    return format_agents_response(
        self._AGENT_NAME, "success", f"Modify Round {attempt + 1}: Success!", None
    )


def _failure_response(self, attempts: int, message: str) -> XResponse:
    logger.error(f"Failed after {attempts} attempts: {message}")
    return format_agents_response(
        self._AGENT_NAME, "fail", f"Modify Round {attempts}: {message}", None
    )


class ExecutionResult:
    """Helper class to encapsulate execution outcomes"""

    def init(self, success: bool, message: str):

        self.success = success

        self.message = message
