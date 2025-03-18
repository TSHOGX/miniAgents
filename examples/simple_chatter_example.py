import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.simple_chatter import SimpleChatter


def main():

    chatter = SimpleChatter()
    while True:
        # get user input
        prompt = input("You: ")

        if prompt == "q":
            break

        result = chatter.run(prompt)
        print(f"🤖: {result}")

    # Show the conversation history
    print("\n======= Conversation History =======")
    for msg in chatter.memory.messages:
        print(f"{msg.role.capitalize()}: {msg.content}")


if __name__ == "__main__":
    main()
