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
including table names and field descriptions. Please answer the user's questions about this database.**

## Database Information

{table_description}

## User Questions

{user_queries}

## Output Requirements
1. Understand the user's questions, they may be a series of instructions. For complex questions, extract the key points first.
2. Understand the database structure, select appropriate tables, and based on the field descriptions, answer the user's question.
"""


PROMPTS[
    "GENERATE_SQL"
] = """Generate a SQL query based on the following infomations. User may give multiple instructions, you need to generate a SQL query that addresses all user's requests.

Table schema:
{table_schema}

Helper information:
{helper_info}

User requests: 
{user_query}

Requirements:
1. Write a valid SQL query that addresses all user's instructions
2. Include appropriate filtering, grouping, and ordering based on the question
3. Only use fields that exist in the schema
4. If have multiple time columns, make sure they are merged into a single column (e.g. year, month, day) and appears in the first column of the result
5. The table is from Supabase database and the table name is "{table_name}"

Return only the SQL query, no explanations.
"""


PROMPTS[
    "ANALYZE_SQL"
] = """Based on the following query results and the user's questions, provide an informative response.

User questions:
{user_query}

Query results(first 5 rows):
{formatted_data}

Please provide:
1. A direct answer to the user's questions
2. Any relevant insights from the data
3. Provide visualization suggestions based on the data
4. Keep your response concise and focused on the data

Consider what visualization would best represent the data. Some guidelines:
- Bar charts: Good for comparing quantities across categories
- Line charts: Ideal for showing trends over time or continuous variables
- Pie charts: Effective for showing proportions or percentages of a whole
- Scatter plots: Good for showing relationships between two numeric variables
- Heatmaps: Useful for showing complex data relationships or color-coding values
- Box plots: Helpful for comparing distributions or identifying outliers

Response:"""


PROMPTS[
    "FIX_SQL"
] = """Based on the following error message, fix the SQL query.

Error message: {error_message}

Table schema:
{table_schema}

```sql
{sql_code}
```

Please fix the SQL code to resolve this error. Only return the corrected SQL code, no explanations.
"""


PROMPTS[
    "GET_TABLE_NAME"
] = """Based on the following table descriptions and user query, determine which table should be used:

Table descriptions:
{db_info}

User query: {query}

First, analyze what information the user is looking for.
Then, determine which table contains the necessary fields to answer the query.
Respond with just the table name, nothing else.
"""
