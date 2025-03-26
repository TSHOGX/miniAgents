import sys
import os
import json

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import LLMSettings
from app.llm import LLM
from app.schema import Message
from app.tools.sql_debugger import fix_sql, get_sql_debugger_tool


def main():
    # Initialize the LLM
    llm = LLM(config_name="coder")

    # Example SQL with an error
    sql_code = """
    SELECT * FROM transactions 
    WHERE amount > 100 
    ORDER BY unknown_column
    """
    error_message = "column unknown_column does not exist"

    # Define the SQL debugger tool
    tools = [get_sql_debugger_tool()]

    # Use the tool to fix the SQL
    response = llm.ask_tool(
        [
            Message.user(
                f"Fix this SQL code that has an error: {error_message}\n\n{sql_code}"
            ),
        ],
        tools=tools,
    )

    print("\nLLM Response:")
    print(response)

    # Check if there are tool calls
    if response.tool_calls:
        print("\nTool was called!")

        # Process each tool call
        for tool_call in response.tool_calls:
            if tool_call.function.name == "fix_sql":
                # Parse tool call arguments
                args = json.loads(tool_call.function.arguments)
                sql_code = args.get("sql_code")
                error_message = args.get("error_message")

                # Call the tool function
                fixed_sql = fix_sql(sql_code, error_message, llm)

                # Send the fixed SQL back to the LLM
                final_response = llm.ask(
                    [
                        Message.user(
                            f"Fix this SQL code that has an error: {error_message}\n\n{sql_code}"
                        ),
                        Message.tool(
                            content=fixed_sql,
                            name="fix_sql",
                            tool_call_id=tool_call.id,
                        ),
                    ],
                    stream=False,
                )

                print("\nFixed SQL:")
                print(fixed_sql)
                print("\nFinal Response:")
                print(final_response)


if __name__ == "__main__":
    main()
