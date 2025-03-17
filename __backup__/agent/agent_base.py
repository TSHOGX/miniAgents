# from .agent import Agent
# from litellm.types.utils import ModelResponse
# from litellm import CustomStreamWrapper
# from typing import Union


# class BaseChatter(Agent):
#     """Handles chat interactions with configurable streaming support"""

#     def work(
#         self, query: str, stream: bool = False
#     ) -> Union[ModelResponse, CustomStreamWrapper]:
#         """Process a user query and return the LLM response.

#         Args:
#             query: User input message
#             stream: Whether to return a streaming response

#         Returns:
#             ModelResponse or streaming wrapper depending on stream flag
#         """
#         if stream:
#             return self.get_response_stream(query)
#         return self.get_response(query)
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, TypedDict
from llm.llm_base import LLMBase

# from loguru import logger


class XContent(TypedDict):
    result_path: Optional[str]
    message: Optional[str]


class XResponse(TypedDict):
    name: str
    status: str
    content: XContent


def format_agents_response(
    name: str,
    status: str,
    message: Optional[str] = None,
    result_path: Optional[str] = None,
) -> XResponse:
    return {
        "name": name,
        "status": status,
        "content": {
            "message": message,
            "result_path": result_path,
        },
    }


class Agent(ABC):
    """Agent is the minimal unit to have llm model interaction.
    - An Agent should have its own workflow
    - Base class provide the basic methods to get response and add to default memory
    """

    def __init__(self, agent_name: str, llm_model: LLMBase):
        self.agent_name = agent_name
        self.llm_model = llm_model

    @abstractmethod
    def work(self, *args, **kwargs):
        raise NotImplementedError
