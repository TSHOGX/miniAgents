"""
Prompt templates for NL2SQL agent workflow.
"""

# Prompt to identify relevant tables for a query
CHOOSE_TABLE_PROMPT = """You are a database expert tasked with identifying the most relevant tables for a natural language query.

Here are the available tables in our database:
{table_schemas}

User Query: {query}

Select the most relevant table(s) for answering this query. For each table, list it in the format:
database_name.table_name

Only list tables that actually exist in the schema information provided above. Be precise with names.
"""

# Prompt to generate SQL from a user query
WRITE_SQL_PROMPT = """You are a SQL expert for Clickhouse database systems. Generate a SQL query to answer the user's question.

Available table(s) and schema(s):
{table_schemas}

User Query: {query}

User Feedback (if any): {feedback}

Clickhouse SQL Query Requirements:
1. Use only fields that exist in the provided schema
2. Follow Clickhouse SQL syntax (not MySQL, PostgreSQL, etc.)
3. Use appropriate Clickhouse functions when needed
4. Ensure proper joins if multiple tables are used
5. Use aliases for clarity when appropriate
6. Include appropriate WHERE clauses to filter data as needed
7. Format the query for readability

Output your SQL query code inside ```sql code blocks.
"""

# Prompt to validate SQL against schema and Clickhouse requirements
CHECK_SQL_PROMPT = """You are a SQL validation expert for Clickhouse databases. Review the SQL code for correctness.

Available table(s) and schema(s):
{table_schemas}

SQL Code to Validate:
```sql
{sql_code}
```

Validation tasks:
1. Check that all column names exist in the referenced tables
2. Verify that joins use correct column names
3. Confirm that table references are valid
4. Validate that all Clickhouse functions are used correctly
5. Check that data types are handled appropriately
6. Verify syntax correctness for Clickhouse SQL

If the SQL is valid, respond with "VALID: The SQL query is correct."
If the SQL is invalid, respond with "INVALID: Reason: [detailed explanation of errors]"
"""

# Complete set of prompts for the NL2SQL agent
NL2SQL_PROMPTS = {
    "choose_table": CHOOSE_TABLE_PROMPT,
    "write_sql": WRITE_SQL_PROMPT,
    "check_sql": CHECK_SQL_PROMPT,
}
