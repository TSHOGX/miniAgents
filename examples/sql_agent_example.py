import sys
import os

# Add the project root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents import SQLAgent


def main():
    # Create a SQL agent
    agent = SQLAgent()

    # Run the agent with a query
    print("Example 1: Simple SQL Query")
    response = agent.run("Show me transactions with amounts over $100")
    print(f"Response: {response}\n")
    print("-" * 100)

    # Run another query to demonstrate the agent's ability to handle different requests
    print("Example 2: Aggregation Query")
    response = agent.run("Calculate the total transaction amount by category")
    print(f"Response: {response}\n")
    print("-" * 100)

    # Run a query that might generate an error to demonstrate error handling
    print("Example 3: Query with Potential Error")
    response = agent.run("List all transactions sorted by unknown_column")
    print(f"Response: {response}\n")
    print("-" * 100)

    # Interactive mode
    print("Interactive mode (type 'exit' to quit):")
    agent.memory.clear()  # Clear memory for a fresh start
    while True:
        query = input("🧐: ")
        if query.lower() in ("exit", "quit", "q"):
            break
        response = agent.run(query)
        print(f"🤖: {response}\n")
        print("-" * 100)


if __name__ == "__main__":
    main()
