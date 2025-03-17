agents_info_vllm = {
    "Decision Maker": {
        "agent_name": "Decision Maker",
        "type": "DecisionMaker",
        "system_prompt": "你是 XAgents, 一个数据分析专家, 管理着一个数据平台团队, 负责回答用户对数据库 `XPlatform` 的基本问题, 分析其中的数据表, 生成或修复 SQL 代码, 生成可视化等任务, 也可以进行日常的对话.",
        "model": "hosted_vllm/Qwen/Qwen2.5-Coder-7B-Instruct",
        "api_base": "http://localhost:8000/v1",
        "api_key": "xagents-coder",
        "temperature": 0.8,
    },
    "SQL Generator": {
        "agent_name": "SQL Generator",
        "type": "SQLGenerator",
        "system_prompt": "You are a SQL and ClickHouse expert. You can generate ClickHouse code based on user's input.",
        "model": "hosted_vllm/Qwen/Qwen2.5-Coder-7B-Instruct",
        "api_base": "http://localhost:8000/v1",
        "api_key": "xagents-coder",
        "temperature": 0.8,
    },
    "SQL Modifier": {
        "agent_name": "SQL Modifier",
        "type": "SQLModifier",
        "system_prompt": "You are a ClickHouse and SQL expert. You can modify the SQL code to make it work.",
        "model": "hosted_vllm/Qwen/Qwen2.5-Coder-7B-Instruct",
        "api_base": "http://localhost:8000/v1",
        "api_key": "xagents-coder",
        "temperature": 0.8,
    },
    "DB Info Manager": {
        "agent_name": "DB Info Manager",
        "type": "GetDbInfo",
        "system_prompt": "You are a SQL expert. You can generate MySQL code based on user's input.",
        "model": "hosted_vllm/Qwen/Qwen2.5-Coder-7B-Instruct",
        "api_base": "http://localhost:8000/v1",
        "api_key": "xagents-coder",
        "temperature": 0.8,
    },
}


agents_info = agents_info_vllm


###

# Common base configuration for all agents
BASE_CONFIG = {
    "model": "hosted_vllm/Qwen/Qwen2.5-Coder-7B-Instruct",
    "api_base": "http://localhost:8000/v1",
    "api_key": "xagents-coder",
    "temperature": 0.8,
}

# Agent-specific configurations
AGENT_CONFIGS = {
    "decision_maker": {
        "agent_name": "Decision Maker",
        "type": "DecisionMaker",
        "system_prompt": (
            "You are XAgents, a data analysis expert managing a data platform team. "
            "Your responsibilities include answering database queries, analyzing data tables, "
            "generating/fixing SQL code, creating visualizations, and handling general conversations."
        ),
    },
    "sql_generator": {
        "agent_name": "SQL Generator",
        "type": "SQLGenerator",
        "system_prompt": (
            "You are a SQL and ClickHouse expert. "
            "Generate efficient ClickHouse code based on user requirements."
        ),
    },
    "sql_modifier": {
        "agent_name": "SQL Modifier",
        "type": "SQLModifier",
        "system_prompt": (
            "You are a ClickHouse specialist. "
            "Modify and optimize SQL code to resolve errors and improve performance."
        ),
    },
    "db_info_manager": {
        "agent_name": "DB Info Manager",
        "type": "GetDbInfo",
        "system_prompt": (
            "You are a database schema expert. "
            "Provide detailed information about database structure and contents."
        ),
    },
}

# Generate final config by merging base and specific configurations
agents_info = {key: {**BASE_CONFIG, **config} for key, config in AGENT_CONFIGS.items()}
