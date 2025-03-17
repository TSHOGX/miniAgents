# NL2SQL Agent Workflow

A workflow for converting natural language questions to SQL queries for Clickhouse databases.

## Overview

This agent workflow processes natural language questions about data and converts them to SQL queries that can be executed against a Clickhouse database. The workflow handles:

1. Identifying relevant database tables based on the question
2. Writing a SQL query based on the table schema and question
3. Validating the SQL for correctness (field names, Clickhouse functions)
4. Executing the SQL and returning results or error information
5. Handling user feedback for query refinement

## Components

### Files

- `agent/nl2sql_agent.py`: Main agent implementation with the workflow logic
- `nl2sql_prompts.py`: Prompt templates for each step of the process
- `nl2sql_example.py`: Example usage of the NL2SQL agent

### Classes

- `NL2SQLAgent`: The main agent class that implements the workflow
- Inherits from the base `Agent` class

## Workflow Steps

### 1. Choose Table

The agent analyzes the user's question and identifies the most relevant database tables.

**Input**:
- User's natural language question
- Available table schemas

**Output**:
- List of relevant (database_name, table_name) tuples

### 2. Write SQL

The agent generates a SQL query based on the identified tables and the user's question.

**Input**:
- User's natural language question
- Relevant table schemas
- Optional user feedback

**Output**:
- SQL query string

### 3. Check SQL

The agent validates the SQL query for correctness against the database schema and Clickhouse syntax requirements.

**Input**:
- Generated SQL query
- Relevant table schemas

**Output**:
- Validation result (boolean)
- Validation message

### 4. Execute SQL

The agent executes the SQL query against the Clickhouse database.

**Input**:
- Validated SQL query

**Output**:
- Execution result ("success" or error message)
- Data if successful

### 5. Handle Results

The agent processes the execution results and returns appropriate information to the user.

**If successful**:
- Returns SQL code and data results

**If failed**:
- Returns SQL code and error information
- Invites user intervention

## Configuration

### Table Schemas

Table schemas should be provided in the following format:

```python
{
    "database_name": {
        "table_name": {
            "columns": [
                {"name": "column_name", "type": "data_type", "description": "description"},
                # Additional columns...
            ],
            "description": "Table description"
        },
        # Additional tables...
    },
    # Additional databases...
}
```

### Prompts

The agent uses specific prompts for each step of the workflow:

- `choose_table`: Prompt for identifying relevant tables
- `write_sql`: Prompt for generating SQL code
- `check_sql`: Prompt for validating SQL code

## Example Usage

```python
from agent.nl2sql_agent import NL2SQLAgent
from nl2sql_prompts import NL2SQL_PROMPTS
from llm.llm_openai import OpenAILLM

# Initialize LLM
llm = OpenAILLM(
    model_name="gpt-4",
    api_key="your_api_key",
    api_base="https://api.openai.com/v1"
)

# Initialize NL2SQL agent
nl2sql_agent = NL2SQLAgent(
    agent_name="NL2SQL Agent",
    llm_model=llm,
    table_schemas=YOUR_TABLE_SCHEMAS,
    prompts=NL2SQL_PROMPTS
)

# Process a query
response = nl2sql_agent.work("How many users registered last month?")

# Handle feedback if needed
if response["status"] == "failure":
    feedback = "Please use date_trunc('month', registration_date) for month grouping"
    response = nl2sql_agent.work("How many users registered last month?", feedback)
```

## Extension Points

The NL2SQL agent can be extended in several ways:

1. Adding support for more database types beyond Clickhouse
2. Implementing more sophisticated SQL validation
3. Adding a query optimization step
4. Implementing automated error correction
5. Integrating with data visualization tools

## Dependencies

- A language model (e.g., OpenAI GPT-4)
- Clickhouse database
- Python 3.9+ 