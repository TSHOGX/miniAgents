import sys
import os

# Add the project root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents import SQLAgent
from app.prompts.db_info import DB_INFO


def main():
    # Create a Supabase transaction agent
    agent = SQLAgent(
        table_schema=DB_INFO["TABLE_SCHEMA"],
        db_info=DB_INFO["DB_INFO"],
        helper_info=DB_INFO["HELPER_INFO"],
    )

    while True:
        question = input("🥳: ")
        if question == "q":
            break
        response = agent.run(question)
        # agent.memory.clear()
        print(agent.memory.to_dict_list())
        print(agent.memory.curr_df())
        print(f"🤖: {response}")
        print("-" * 100)


if __name__ == "__main__":
    main()
