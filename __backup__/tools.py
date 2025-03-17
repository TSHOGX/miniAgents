import re
from typing import TypedDict, Optional

import pandas as pd
from utils import Database


db = Database()


def tool_excute_sql(sql: str) -> str:
    """return error message or success; save dataframe and sql code to data/memory/df.parquet and data/memory/sql_code.sql"""
    # db = Database()

    try:
        df: pd.DataFrame = db.fetch_dataframe(sql)
        df.to_parquet("data/memory/df.parquet")
        with open("data/memory/sql_code.sql", "w") as f:
            f.write(sql)
        resp = "success"
    except Exception as e:
        resp = str(e)

    # db.close()
    return resp


# sql_code = """
# SELECT COUNT(DISTINCT VEHICLE_ID) AS vehicle_count
# FROM hw_x_vhr_vehicle_condition_charge_t;
# """

# print(tool_excute_sql(sql_code))

# def tool_fix_sql_by_error(error_message: str):
#     # fix errors
#     return {
#         "name": "tool_fix_sql_by_error",
#         "status": "success",
#         "content": {
#             "sql": "SELECT * FROM charge_data",
#             "message": "Fixed successfully",
#         },
#     }


def tool_extract_sql_list(response: str) -> list:
    matches = re.findall(r"```sql\n(.*?)```", response, re.DOTALL)
    queries = []
    for match in matches:
        match = match.strip()
        if match[-1] == ";":
            match = match.strip()[:-1]
        queries.append(match)
    return queries


###

import re
import os
from pathlib import Path
from typing import List, Optional
import pandas as pd
from utils import Database, logger

# Configure paths
MEMORY_DIR = Path("data/memory")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
DF_PATH = MEMORY_DIR / "df.parquet"
SQL_CODE_PATH = MEMORY_DIR / "sql_code.sql"


def tool_execute_sql(sql: str, save_results: bool = True) -> str:
    """Execute SQL query and handle results safely.

    Args:
        sql: Valid SQL query string
        save_results: Whether to persist results to disk

    Returns:
        "success" or error message string
    """
    try:
        with Database() as db:
            df = db.fetch_dataframe(sql)

            if save_results:
                df.to_parquet(DF_PATH)
                SQL_CODE_PATH.write_text(sql, encoding="utf-8")

            return "success"

    except Exception as e:
        logger.error(f"SQL execution failed: {str(e)}")
        return f"Execution Error: {str(e)}"


def tool_extract_sql_list(response: str) -> List[str]:
    """Extract and clean SQL code blocks from text response.

    Args:
        response: Text potentially containing SQL code blocks

    Returns:
        List of cleaned SQL queries
    """
    # Case-insensitive match for SQL code blocks
    sql_blocks = re.findall(
        r"```sql\n(.*?)```", response, flags=re.DOTALL | re.IGNORECASE
    )

    return [clean_sql_block(block) for block in sql_blocks]


def clean_sql_block(block: str) -> str:
    """Sanitize SQL code block"""
    cleaned = block.strip()

    # Remove trailing semicolon and whitespace
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].rstrip()

    return cleaned
