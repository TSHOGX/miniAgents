# Test the LLM

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import LLMSettings
from app.llm import LLM
from app.schema import Message


# temp_llm_config = LLMSettings(
#     model="qwen2.5-coder:7b",
#     base_url="http://localhost:11434/v1",
#     api_key="ollama",
#     max_tokens=4096,
#     temperature=0.5,
# )


def main():
    # temp_llm_config = LLMSettings(
    #     model="qwen2.5-coder:7b",
    #     base_url="http://localhost:11434/v1",
    #     api_key="ollama",
    #     max_tokens=4096,
    #     temperature=0.5,
    # )
    # llm = LLM(config_name="coder", llm_config=temp_llm_config)

    llm = LLM(config_name="coder")
    llm.ask(
        [
            Message.user("Hello, my name is Shiwen Han."),
            Message.assistant("Hi, Shiwen Han. How can"),
            Message.user("continue the conversation"),
        ],
        stream=True,
    )


if __name__ == "__main__":
    main()
