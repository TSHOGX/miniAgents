from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
)

response = client.chat.completions.create(
    model="qwen2.5-coder:7b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The LA Dodgers won in 2020."},
        {"role": "user", "content": "Where was it played?"},
    ],
)
print(response.choices[0].message.content)


class OllamaLLM:
    def __init__(self, model: str):
        self.model = model

    def build_messages(self, prompt: str, system_prompt: str | None) -> list[dict]:
        user_msg = {"role": "user", "content": prompt}
        if system_prompt:
            return [
                {"role": "system", "content": system_prompt},
                user_msg,
            ]
        return [user_msg]

    def get_content(self, response, is_stream: bool) -> str:
        if is_stream:
            content = ""
            for chunk in response:
                if content_chunk := chunk["choices"]["delta"].get("content"):
                    content += content_chunk
            return content
        return response["choices"]["message"]["content"]

    def get_completion(self, prompt: str, system_prompt: str | None, stream: bool):
        raise NotImplementedError
