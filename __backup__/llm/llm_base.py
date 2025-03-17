from abc import ABC, abstractmethod


class LLMBase(ABC):
    def __init__(self, model_name: str, api_key: str, api_base: str):
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base

    @abstractmethod
    def get_completion(self, msgs, stream: bool):
        raise NotImplementedError

    @abstractmethod
    def get_response(self, msgs, stream: bool = False) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_content(self, response, is_stream: bool):
        raise NotImplementedError

    @abstractmethod
    def build_messages(self, prompt: str, system_prompt: str | None) -> list[dict]:
        raise NotImplementedError
