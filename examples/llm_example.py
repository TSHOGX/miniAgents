# Test the LLM

import sys
import os
import json

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


# 定义工具函数
def get_weather(location):
    """
    获取指定城市的天气信息

    Args:
        location: 城市名称

    Returns:
        天气信息字符串
    """
    # 这里是模拟数据，实际应用中可以调用天气API
    weather_data = {
        "Shanghai": {"temperature": "26°C", "condition": "晴朗", "humidity": "65%"},
        "Beijing": {"temperature": "24°C", "condition": "多云", "humidity": "55%"},
        "Guangzhou": {"temperature": "30°C", "condition": "小雨", "humidity": "80%"},
    }

    if location in weather_data:
        data = weather_data[location]
        return f"{location}的天气：{data['temperature']}，{data['condition']}，湿度{data['humidity']}"
    else:
        return f"抱歉，没有找到{location}的天气信息"


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

    # 定义天气查询工具
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the weather in a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "要查询天气的城市名称",
                        }
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    # 使用工具处理用户查询
    response = llm.ask_tool(
        [
            Message.user("What is the weather in Shanghai?"),
        ],
        tools=tools,
    )

    print("\nLLM Response:")
    print(response)

    # 检查是否有工具调用
    if response.tool_calls:
        print("\nTool was called!")

        # 处理每个工具调用
        for tool_call in response.tool_calls:
            if tool_call.function.name == "get_weather":
                # 解析工具调用参数
                args = json.loads(tool_call.function.arguments)
                location = args.get("location")

                # 调用工具函数
                tool_response = get_weather(location)

                # 将工具响应发送回LLM
                final_response = llm.ask(
                    [
                        Message.user("What is the weather in Shanghai?"),
                        Message.tool(
                            content=tool_response,
                            name="get_weather",
                            tool_call_id=tool_call.id,
                        ),
                    ],
                    stream=False,
                )

                print("\nFinal Response (after tool use):")
                print(final_response)


if __name__ == "__main__":
    main()
