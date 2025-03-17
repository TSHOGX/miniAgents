PROMPTS = {}

PROMPTS[
    "decision_maker_summary"
] = """Summarize the following list of queries into a single query. 
Do not add new information, just combine relevant queries concisely.

Examples:
Query List: ["天气真好!"]
Summarized Query: 天气真好!

Query List: ["查询车辆所有ID", "修改一下, 添加每个车的充电时长", "我想知道每辆车的平均充电DOD"]
Summarized Query: 查询所有车辆ID，并添加每辆车的充电时长，以及每辆车的平均充电DOD。

Current Query List: {query_list}
Summarized Query: """

PROMPTS[
    "decision_maker_worker"
] = """Assign the task to one of these workers: {worker_names}. 
Worker descriptions: {worker_list}.

Examples:
Question: 数据表里有多少车辆 → get_sql
Question: 数据表有什么字段 → get_db_info
Question: 今天天气真好 → base_chat

Current Question: {query}
Worker: """


PROMPTS[
    "get_db_info"
] = """**As a professional data analyst, answer user questions about the database using the following schema:**

## Database Schema
{table_description}

## User Question
{query}

## Requirements
1. Analyze complex questions by extracting key points
2. Select appropriate tables/columns based on schema understanding
3. Provide clear, structured responses using markdown formatting"""
