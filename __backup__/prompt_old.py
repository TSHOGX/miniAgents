modify_sql_by_user = """I will provide the user's series of questions (including the original question and any supplementary details), along with the current SQL code and the user's new input. Based on this information, as well as the field descriptions of the database tables, you need to modify or regenerate the SQL code accordingly:

### Table Field Descriptions
{table_description}

### User's Question List
{question_list}

### SQL Code
```sql
{sql_code}
```

### New User Input
{curr_user_prompt}
"""


decision_maker_extract_new_query = """Summarize the following list of queries into a single query. Do not add any new information or details, just combine relevant queries into a concise form.

Query List: ["天气真好!"]
Summarized Query: 天气真好!

Query List: ["查询车辆所有ID", "修改一下, 添加每个车的充电时长", "我想知道每辆车的平均充电DOD"]
Summarized Query: 查询所有车辆ID，并添加每辆车的充电时长，以及每辆车的平均充电DOD。

Begin!

Query List: {query_list}
Summarized Query: """

decision_maker_query = """Try your best to assign the task to the following employees: {worker_names}. 
The description of the employees are: {worker_list}.
The memories you have are: [].

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


sql_generator_query = """**你是专业的数据分析科学家，精通 SQL 语言和 ClickHouse。请根据以下数据表字段说明和用户需求编写精确的 ClickHouse 代码（表名: `{tbl_name}`）。**

### 任务要求：
1. 逐步分析用户需求并提取关键要点。
   - 理解字段含义, 明确字段使用, 使用规范化后的字段。
   - 定义过滤条件。
   - 识别聚合逻辑或排序方式等核心逻辑。
2. 优化需求描述以减少语义模糊，确保 SQL 查询的准确性。
3. 输出的 SQL 查询应遵循最佳实践，语法正确，性能优化。

### 输入内容
#### 用户需求:
{query}

#### 字段说明:
{table_description[f"{tbl_name}"]}

### 输出内容
1. 使用 Markdown 格式输出生成的 ClickHouse 查询代码
2. 注意 ClickHouse 的代码不要添加末尾的分号
3. 对于 String 类型的字段, 可以考虑用`toFloat64(VARIABLE_NAME)`转化成数值
4. 对于时间类型的字段, 可以考虑用类似`toStartOfWeek`, `toDate`之类的function转化成所需值

### 示例
```sql
SELECT ... 
FROM {tbl_name}
WHERE ... 
GROUP BY ...
ORDER BY ...
```
"""
# ### 输出内容
# 1. 简要分析用户需求并列出关键要点。
# 2. 使用 Markdown 格式输出生成的 ClickHouse 查询代码。
# 3. 注意 ClickHouse 的代码不要添加末尾的分号, 且一次只生成一段查询。


sql_generator_get_tbl_name_query = """**你是专业的数据分析科学家, 请根据以下数据表字段说明和用户需求, 选择正确的数据表名**

## 表字段说明

{table_description}

## 任务

请根据问题的语义和各个表格包含的字段, 找到与问题最相关的数据表, 告知用户正确的表名.

Question: 统计不同类型的车的每周充电时长
Table Name: hw_x_vhr_vehicle_condition_charge_t

Question: 利用表格 (hw_x_vhr_vehicle_condition_run_t), 统计不同车放电DOD的分布
Table Name: hw_x_vhr_vehicle_condition_run_t

Begin!

Question: {query}
Table Name: """


sql_modifier_query = """Please modify the SQL code based on my instruction. Notice that the instruction can be a suggestion or a requirement provided by user, or a error info generated automatically.

SQL platform: ClickHouse

Instruction: {instruction}

Code:
```sql
{sql_code}
```

Modified Code:
"""

query_store_formatted_query = """请判断用户的提问是属于继续当前任务的补充，还是开启一个新的任务. 一个任务通常是一个独立的问题，可能包含寻常对话、SQL查询、代码修改等内容。需要特别注意的是，SQL查询或代码修改中的多个用户提问可能是对同一任务的补充，尤其当用户对查询结果或代码修改提出细节调整时. 请根据用户提问的语义, 判断是否属于任务的补充信息, 如果是, 则返回 True; 如果不是补充信息, 则返回 False.

例如：

User: 今天天气真好
Assistant: False

User: 不, 我想要的变量是xxx, 不是xxx
Assistant: True

User: 修改一下, 我想要增加一个充放电的分类
Assistant: True

User: 我想要额外统计一个变量, 充电时长
Assistant: True

User: 统计不同车辆的速度分布
Assistant: False

User: 查询车辆的充电时长
Assistant: False

Begin!

User: {query}
Assistant: """


get_db_info_formated_query = """**你是专业的数据分析科学家, 我会提供给你数据库的信息, 包括数据表名, 和对应的字段说明. 请回答用户关于这个数据库的问题.**

## 数据库信息

{table_description}

## 用户问题

{query}

## 输出要求
1. 理解用户提问, 对于复杂的提问, 可以先提取关键要点.
2. 理解数据库结构, 选择合适的表格, 然后根据字段说明, 基于理解回答用户问题.
"""


###

# SQL Modification Prompt
MODIFY_SQL_PROMPT = """**Task**: Modify existing SQL code based on new requirements

**Database Schema**
{table_description}

**User Query History**
{question_list}

**Current SQL Code**
```sql
{sql_code}
```

**New Instruction**
{curr_user_prompt}

**Requirements**
1. Maintain original query intent
2. Implement new requirements precisely
3. Validate against schema constraints
4. Keep ClickHouse syntax compliance
"""

# Query Summarization Prompt
QUERY_SUMMARY_PROMPT = """**Task**: Consolidate related queries into single request

**Examples**
- Input: ["天气真好!"] → Output: 天气真好!
- Input: ["查询车辆所有ID", "修改添加充电时长", "平均充电DOD"] 
  → Output: 查询所有车辆ID，添加充电时长及平均充电DOD

**Current Queries**
{query_list}

**Consolidated Query**
"""

# Worker Assignment Prompt
WORKER_ASSIGNMENT_PROMPT = """**Task**: Route query to appropriate specialist

**Available Experts**
{worker_list}

**Examples**
1. 数据表里有多少车辆 → get_sql
2. 数据表字段信息 → get_db_info  
3. 日常对话 → base_chat
4. 充电统计 → get_sql

**Current Query**
{query}

**Selected Expert**
"""

# SQL Generation Prompt
SQL_GEN_PROMPT = """**Role**: ClickHouse Expert

**Task**: Generate optimized SQL from requirements

**Schema**
{table_description}

**Requirements**
1. Analyze query intent
2. Identify required fields/metrics
3. Define filters/aggregations
4. Optimize performance

**Output Format**
```sql
-- ClickHouse-compliant code
SELECT ...
FROM {tbl_name}
```

**User Request**
{query}
"""

# Table Identification Prompt
TABLE_ID_PROMPT = """**Task**: Identify relevant database table

**Schema**
{table_description}

**Examples**
1. 统计每周充电时长 → hw_x_vhr_vehicle_condition_charge_t
2. 车放电DOD分布 → hw_x_vhr_vehicle_condition_run_t

**Current Query**  
{query}

**Matched Table**
"""

# Context Detection Prompt
CONTEXT_DETECT_PROMPT = """**Task**: Determine query context

**Guidelines**
✅ CONTINUE if:
- Modifies previous request 
- Adjusts filters/metrics
- Fixes errors

🆕 NEW if:  
- Different analysis focus
- Unrelated question
- New dataset request

**Examples**
1. 增加充放电分类 → CONTINUE
2. 统计速度分布 → NEW

**Current Query**
{query}

**Decision**
"""

# Schema Query Prompt
SCHEMA_QUERY_PROMPT = """**Role**: Database Analyst

**Schema**
{table_description}

**Task**: Answer schema-related questions

**Process**  
1. Parse question requirements
2. Match schema elements
3. Provide structured response

**User Question**
{query}
"""
