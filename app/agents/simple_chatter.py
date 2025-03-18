from app.agents.base import BaseAgent


class SimpleChatter(BaseAgent):
    """A simple chat agent that responds to user messages."""

    name: str = "SimpleChatter"
    description: str = "A simple chat agent that responds to user messages."
    system_prompt: str = "You are a helpful assistant that responds to user messages."
    next_step_prompt: str = ""

    def step(self) -> str:
        """Execute a single step in the conversation."""
        # Get the last message from memory
        messages = self.memory.to_dict_list()

        # Generate a response using the LLM
        response = self.llm.ask(
            messages=messages,
            temperature=0.7,
            stream=False,
        )

        # Store the response in memory
        self.update_memory("assistant", response)

        return response
