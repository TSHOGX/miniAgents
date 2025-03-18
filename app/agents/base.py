from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.llm import LLM
from app.schema import Memory, Message


class BaseAgent(BaseModel, ABC):
    """Abstract base class for managing agent state and execution.

    Provides foundational functionality for state transitions, memory management,
    and a step-based execution loop. Subclasses must implement the `step` method.
    """

    # Core attributes
    name: str = Field(..., description="Unique name of the agent")
    description: Optional[str] = Field(None, description="Optional agent description")

    # Prompts
    system_prompt: Optional[str] = Field(
        None, description="System-level instruction prompt"
    )
    next_step_prompt: Optional[str] = Field(
        None, description="Prompt for determining next action"
    )

    # Dependencies
    llm: LLM = Field(default_factory=LLM, description="Language model instance")
    memory: Memory = Field(default_factory=Memory, description="Agent's memory store")

    # Execution control
    max_steps: int = Field(default=10, description="Maximum steps before termination")
    current_step: int = Field(default=0, description="Current step in execution")

    duplicate_threshold: int = 2

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields for flexibility in subclasses

    @model_validator(mode="after")  # type: ignore
    def initialize_agent(self) -> "BaseAgent":
        """Initialize agent with default settings if not provided."""
        if self.llm is None or not isinstance(self.llm, LLM):
            self.llm = LLM(config_name=self.name.lower())
        if not isinstance(self.memory, Memory):
            self.memory = Memory()
        return self

    def run(self, request: Optional[str] = None) -> str:
        """Execute the agent's main step.

        Can be extended to include more complex logic, e.g. workflow loops.
        """
        # Add request to memory first
        if request:
            self.update_memory("user", request)

        step_result = self.step()

        return step_result

    @abstractmethod
    def step(self) -> str:
        """Execute a single step in the agent's workflow.

        Must be implemented by subclasses to define specific behavior.
        """

    def update_memory(
        self,
        role,
        content: str,
        **kwargs,
    ) -> None:
        """Add a message to the agent's memory."""
        message_map = {
            "user": Message.user,
            "system": Message.system,
            "assistant": Message.assistant,
            "tool": lambda content, **kw: Message.tool(content, **kw),
        }

        if role not in message_map:
            raise ValueError(f"Unsupported message role: {role}")

        # Create message with appropriate parameters
        if role == "tool":
            self.memory.add_message(message_map[role](content, **kwargs))
        else:
            self.memory.add_message(
                message_map[role](content, **kwargs)
                if kwargs
                else message_map[role](content)
            )
