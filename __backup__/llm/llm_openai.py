from openai import OpenAI
from llm_base import LLMBase
from loguru import logger


class OpenAILLM(LLMBase):
    def __init__(self, model_name: str, api_key: str, api_base: str):
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base

        self.client = OpenAI(
            base_url=self.api_base,
            api_key=self.api_key,
        )

    def build_messages(self, prompt: str, system_prompt: str | None) -> list[dict]:
        user_msg = {"role": "user", "content": prompt}
        if system_prompt:
            return [
                {"role": "system", "content": system_prompt},
                user_msg,
            ]
        return [user_msg]

    def get_content(self, response, stream: bool):
        if stream:
            content = ""
            for chunk in response:
                if content_chunk := chunk["choices"]["delta"].get("content"):
                    content += content_chunk
            return content

        content = response.choices[0].message.content

        # logger.info(f"[{self.model_name}] Response: \n{content}")

        return content

    def get_completion(self, msgs, stream=False):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=msgs,
            stream=stream,
        )
        return response

    def get_response(self, msgs, stream=False) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=msgs,
            stream=stream,
        )
        return self.get_content(response, stream)


if __name__ == "__main__":
    llm = OpenAILLM(
        model_name="qwen2.5-coder:7b",
        api_key="ollama",
        api_base="http://localhost:11434/v1",
    )

    print(
        llm.get_response(
            msgs=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {"role": "assistant", "content": "The LA Dodgers won in 2020."},
                {"role": "user", "content": "Where was it played?"},
            ],
        )
    )
