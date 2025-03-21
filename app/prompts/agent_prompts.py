PROMPTS = {}

PROMPTS[
    "SUMMARIZE_QUERIES"
] = """Summarize the following list of queries into a single query. Do not add any new information or details, just combine relevant queries into a concise form.

Query List: ["天气真好!"]
Summarized Query: 天气真好!

Query List: ["你是谁"]
Summarized Query: 你是谁

Query List: ["查询车辆所有ID", "修改一下, 添加每个车的充电时长", "我想知道每辆车的平均充电DOD"]
Summarized Query: 查询所有车辆ID，并添加每辆车的充电时长，以及每辆车的平均充电DOD。

Begin!

Query List: {query_list}
Summarized Query: """

PROMPTS[
    "ASSIGN_WORKER"
] = """Try your best to assign the task to the following employees: {worker_names}. 
The description of the employees are: {workers}.

Examples:

Question: 数据表里有多少车辆
Worker: get_sql

Question: 数据表有什么字段
Worker: get_db_info

Question: 今天天气真好
Worker: base_chat

Question: 统计 charge_t 中, 车辆每周充电次数的分布情况
Worker: get_sql

Question: 充电时间的分布情况如何
Worker: get_sql

Begin!

Question: {query}
Worker: """


PROMPTS[
    "GET_DB_INFO"
] = """**You are a professional data scientist and analyst. I will provide you with database information, 
including table names and field descriptions. Please answer the user's question about this database.**

## Database Information

{table_description}

## User Question

{last_user_query}

## Output Requirements
1. Understand the user's question. For complex questions, extract the key points first.
2. Understand the database structure, select appropriate tables, and based on the field descriptions, answer the user's question.
"""


PROMPTS[
    "GENERATE_SQL"
] = """Generate a SQL query for the following question about financial transactions.

Table schema:
{table_schema}

Available ledger categories:
{ledger_categories}

User question: {user_query}

Requirements:
1. Write a valid SQL query that addresses the user's request
2. Include appropriate filtering, grouping, and ordering based on the question
3. Consider performance optimization
4. Format your response as valid SQL code only (no explanations)
5. Only use fields that exist in the schema
6. The table name is "transactions"

Return only the SQL query, no explanations.
"""


PROMPTS[
    "ANALYZE_SQL"
] = """Based on the following transaction data and the user's question, provide an informative response.

User question: {user_query}

SQL query executed:
```sql
{sql_query}
```

Query results:
{formatted_data}

Please provide:
1. A direct answer to the user's question
2. Any relevant insights from the data
3. Make the response conversational and helpful
4. Format currency values appropriately with ¥ symbol
5. Keep your response concise and focused on the data

Response:"""


PROMPTS[
    "FIX_SQL"
] = """Based on the following error message, fix the SQL query.

Error message: {error_message}

SQL query:
{sql_query}

Requirements:
1. Fix the SQL query to address the error
2. Keep the SQL query valid
3. Keep the SQL query concise
"""
