from enum import Enum
from typing import Any, List, Literal, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field


class Function(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    """Represents a tool/function call in a message"""

    id: str
    type: str = "function"
    function: Function


class Message(BaseModel):
    """Represents a chat message in the conversation"""

    role: Literal["system", "user", "assistant", "tool"] = Field(...)
    content: Optional[str] = Field(default=None)
    tool_calls: Optional[List[ToolCall]] = Field(default=None)
    name: Optional[str] = Field(default=None)
    tool_call_id: Optional[str] = Field(default=None)

    def __add__(self, other) -> List["Message"]:
        """支持 Message + list 或 Message + Message 的操作"""
        if isinstance(other, list):
            return [self] + other  # type: ignore
        elif isinstance(other, Message):
            return [self, other]
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'"
            )

    def __radd__(self, other) -> List["Message"]:
        """支持 list + Message 的操作"""
        if isinstance(other, list):
            return other + [self]
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(other).__name__}' and '{type(self).__name__}'"
            )

    def to_dict(self) -> dict:
        """Convert message to dictionary format"""
        message = {"role": self.role}
        if self.content is not None:
            message["content"] = self.content
        if self.tool_calls is not None:
            message["tool_calls"] = [tool_call.dict() for tool_call in self.tool_calls]  # type: ignore
        if self.name is not None:
            message["name"] = self.name
        if self.tool_call_id is not None:
            message["tool_call_id"] = self.tool_call_id
        return message

    @classmethod
    def user(cls, content: str) -> "Message":
        """Create a user message"""
        return cls(role="user", content=content)

    @classmethod
    def system(cls, content: str) -> "Message":
        """Create a system message"""
        return cls(role="system", content=content)

    @classmethod
    def assistant(cls, content: Optional[str] = None) -> "Message":
        """Create an assistant message"""
        return cls(role="assistant", content=content)

    @classmethod
    def tool(cls, content: str, name, tool_call_id: str) -> "Message":
        """Create a tool message"""
        return cls(role="tool", content=content, name=name, tool_call_id=tool_call_id)

    @classmethod
    def from_tool_calls(
        cls, tool_calls: List[Any], content: Union[str, List[str]] = "", **kwargs
    ):
        """Create ToolCallsMessage from raw tool calls.

        Args:
            tool_calls: Raw tool calls from LLM
            content: Optional message content
        """
        formatted_calls = [
            {"id": call.id, "function": call.function.model_dump(), "type": "function"}
            for call in tool_calls
        ]
        return cls(
            role="assistant", content=content, tool_calls=formatted_calls, **kwargs  # type: ignore
        )


class Memory(BaseModel):
    """memory storage for messages, sql files, df files, etc."""

    messages: List[Message] = Field(default_factory=list)
    max_messages: int = Field(default=100)
    sql_codes: str = Field(default="")
    df_data: pd.DataFrame = Field(default_factory=pd.DataFrame)

    model_config = {"arbitrary_types_allowed": True}

    def add_message(self, message: Message) -> None:
        """Add a message to memory"""
        self.messages.append(message)
        # Optional: Implement message limit
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def add_messages(self, messages: List[Message]) -> None:
        """Add multiple messages to memory"""
        self.messages.extend(messages)

    def clear(self) -> None:
        """Clear all messages"""
        self.messages.clear()

    def get_recent_messages(self, n: int) -> List[Message]:
        """Get n most recent messages"""
        return self.messages[-n:]

    def to_dict_list(self) -> List[Union[dict, Message]]:
        """Convert messages to list of dicts"""
        return [msg.to_dict() for msg in self.messages]

    def add_sql(self, sql: str) -> None:
        """Add a SQL file to memory"""
        self.sql_codes = sql

    def curr_sql(self) -> str:
        """Get the current SQL file"""
        return self.sql_codes

    def add_df(self, df: pd.DataFrame) -> None:
        """Add a DataFrame to memory"""
        self.df_data = df

    def curr_df(self) -> pd.DataFrame:
        """Get the current DataFrame"""
        return self.df_data
