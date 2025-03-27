# type sql to chat with SQLAgent
# type db to chat with DbInfoAgent
# type new to start new conversation
# type q to quit

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents import SQLAgent, DbInfoAgent, SimpleChatter
from app.prompts.db_info import DB_INFO


def main():
    sql_agent = SQLAgent(
        table_schema=DB_INFO["TABLE_SCHEMA"],
        db_info=DB_INFO["DB_INFO"],
        helper_info=DB_INFO["HELPER_INFO"],
    )
    db_info_agent = DbInfoAgent()
    simple_chatter = SimpleChatter()

    current_agent = simple_chatter

    while True:
        question = input("🥳: ")

        if question == "q":
            break
        elif question == "sql":
            current_agent = sql_agent
            current_agent.memory.clear()
            response = "New SQL Agent is ready"
        elif question == "db":
            current_agent = db_info_agent
            current_agent.memory.clear()
            response = "New DB Info Agent is ready"
        elif question == "new":
            current_agent = simple_chatter
            current_agent.memory.clear()
            response = "New conversation is ready"
        else:
            response = current_agent.run(question)

        print(f"🤖: {response}")
        print("-" * 100)
        print(current_agent.memory.to_dict_list())
        print(f"```sql\n{current_agent.memory.curr_sql()}\n```")
        print(current_agent.memory.curr_df())
        print("-" * 100)


if __name__ == "__main__":
    main()
