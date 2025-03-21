import sys
import os

# Add the project root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.decision_maker import DecisionMaker


def main():
    # Create a decision maker agent
    agent = DecisionMaker()

    # Run the agent with a query
    print("Example 1: SQL Query")
    response = agent.run("数据表里有多少车辆?")
    print(f"Response: {response}\n")
    print(agent.memory.to_dict_list())
    print("-" * 100)

    # Run another query to show query summarization
    print("Example 2: Database Info Query")
    response = agent.run("数据表有什么字段?")
    print(f"Response: {response}\n")
    print(agent.memory.to_dict_list())
    print("-" * 100)

    # Run a general chat query
    print("Example 3: General Chat")
    response = agent.run("今天天气真好!")
    print(f"Response: {response}\n")
    print(agent.memory.to_dict_list())
    print("-" * 100)

    # Run a complex query to test summarization
    print("Example 4: Complex Query with Previous Context")
    response = agent.run("我想知道每辆车的平均充电DOD")
    print(f"Response: {response}\n")
    print(agent.memory.to_dict_list())
    print("-" * 100)

    # Clean up the memory
    agent.memory.clear()
    while True:
        query = input("🧐: ")
        if query == "q":
            break
        response = agent.run(query)
        print(f"🤖: {response}\n")
        print(agent.memory.to_dict_list())
        print("-" * 100)


if __name__ == "__main__":
    main()
