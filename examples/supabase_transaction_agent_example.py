import sys
import os

# Add the project root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.supabase_transaction_agent import SupabaseTransactionAgent


def main():
    # Create a Supabase transaction agent
    agent = SupabaseTransactionAgent()

    while True:
        question = input("🥳: ")
        if question == "q":
            break
        response = agent.run(question)
        agent.memory.clear()
        print(f"🤖: {response}")
        print("-" * 100)


if __name__ == "__main__":
    main()
