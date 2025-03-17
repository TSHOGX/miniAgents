import streamlit as st
import pandas as pd
from utils import logger_filepath, mem_sql_code, mem_query


# 页面配置
st.set_page_config(
    page_title="XAgents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "XAgents for X Platform",
    },
)


if "initialized" not in st.session_state:
    # Initialization code here
    st.session_state.initialized = True

    with open(logger_filepath, "w") as file:
        file.write("")

    mem_query.delete_all()

    mem_sql_code.set_code("-- ask some question to get codes")

    dftemp = pd.DataFrame({"TEST": ["HELLO", "WORLD"]})
    dftemp.to_parquet("data/memory/df.parquet")


st.markdown(
    """
    <style>
    /* 设置整个页面的布局为填充满整个视窗 */
    .reportview-container {
        height: 100vh; /* 100% 视窗高度 */
    }

    /* 设置对话模块区域填满剩余的空间并启用滚动条 */
    .stColumn {
        height: calc(90vh - 200px); /* 让此区域占满剩余空间 */
        overflow-y: auto; /* 超出时显示竖向滚动条 */
    }

    /* 设置右侧内容区域的滚动条 */
    .stContainer {
        height: calc(90vh - 200px); /* 同样让此区域填满剩余空间 */
        overflow-y: auto;
    }

    /* 可以根据需求调整标题大小等 */
    h1, h2, h3 {
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


from agents import DecisionMaker
from prompts.agents_info import agents_info

agent_info = agents_info["Decision Maker"]
agent_executor = DecisionMaker(
    agent_name=agent_info["agent_name"],
    model=agent_info["model"],
    api_base=agent_info["api_base"],
    api_key=agent_info["api_key"],
    temperature=agent_info["temperature"],
    system_prompt=agent_info["system_prompt"],
)

# 布局配置
col1, col2 = st.columns([2, 1])  # 对话模块占 2/3，其他模块占 1/3

# 对话模块
with col1:

    # upper_container = st.container()
    # lower_container = st.container()

    # with lower_container:
    st.title("XAgents")

    chat_container = st.container()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示所有消息
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        # 用户输入后，添加消息到会话
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        # 生成助手回复并显示
        with chat_container.chat_message("assistant"):
            content = agent_executor.work(query=prompt)
            st.markdown(content)

        # 将助手回复添加到会话
        st.session_state.messages.append({"role": "assistant", "content": content})


def read_log_file(file_path):
    with open(file_path, "r") as file:
        ff = file.read()
    return ff


# 中间输出模块和表格/可视化模块（Column2）
with col2:
    zero_container = st.container()
    upper_container = st.container()
    middle_container = st.container()
    lower_container = st.container()

    with zero_container:
        st.title("Example Usage")
        st.markdown(
            """支持多轮对话，可以识别新对话的开始，支持SQL生成（自动debug），支持针对数据库信息的提问

例子1
- 你是谁，你能干什么？
- 今天天气怎么样?
- 数据库里有什么表格
- 这个表格里有什么字段：xxx
- 解释一下上面的字段
- 找到上面字段中，和soc相关的字段

例子2
- 统计不同车辆ID的行驶里程和持续时间
- 修改一下，按照不同week来统计
- 我想按照行驶里程来排序这个结果

例子3
- 统计每周充电时长数据
- 我想按照不同车辆ID去分别统计
- 再加上每周的充电次数
- 再加上另一层分类: 快充或慢充
"""
        )

    with upper_container:
        st.title("Table Results")
        dfst = st.empty()
        dfst.write(pd.read_parquet("data/memory/df.parquet"))

    with middle_container:
        st.title("SQL Results")
        sqlst = st.empty()
        sqlst.markdown(
            f"""```sql
{mem_sql_code.get_code()}
```"""
        )

    with lower_container:
        st.title("Log Viewer")
        logst = st.empty()
        logs = read_log_file(logger_filepath)
        logst.markdown(logs)


###


import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional
from agents import DecisionMaker
from prompts.agents_info import agents_info
from utils import logger_filepath, mem_sql_code, mem_query

# Constants
MEMORY_DIR = Path("data/memory")
DF_PATH = MEMORY_DIR / "df.parquet"
INITIAL_SQL = "-- Ask a question to generate SQL code\n-- Example: Show weekly charging statistics by vehicle"
CSS_PATH = Path("assets/styles.css")

# Page Configuration
st.set_page_config(
    page_title="XAgents Analytics Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "XAgents - Intelligent Data Analytics Platform"},
)


@st.cache_resource
def init_agent() -> DecisionMaker:
    """Initialize and cache the AI agent"""
    config = agents_info["Decision Maker"]
    return DecisionMaker(
        agent_name=config["agent_name"],
        model=config["model"],
        api_base=config["api_base"],
        api_key=config["api_key"],
        temperature=config["temperature"],
        system_prompt=config["system_prompt"],
    )


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load and cache dataset with error handling"""
    try:
        return pd.read_parquet(DF_PATH)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()


def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "initialized": True,
        "messages": [],
        "current_df": None,
        "sql_history": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Initialize system files
    MEMORY_DIR.mkdir(exist_ok=True)
    if not DF_PATH.exists():
        pd.DataFrame({"Status": ["System Initialized"]}).to_parquet(DF_PATH)


def render_chat_interface(agent: DecisionMaker):
    """Main chat interface component"""
    with st.container():
        st.title("XAgents Chat Interface")

        # Chat History
        chat_container = st.container()
        for msg in st.session_state.messages:
            with chat_container.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # User Input
        if prompt := st.chat_input("Enter your data query or request"):
            with st.spinner("Analyzing request..."):
                handle_user_input(prompt, agent, chat_container)


def handle_user_input(prompt: str, agent: DecisionMaker, container):
    """Process user input and display responses"""
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    container.chat_message("user").markdown(prompt)

    try:
        # Generate agent response
        response = agent.work(query=prompt)

        # Update session state
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.current_df = load_data()
        st.session_state.sql_history.append(mem_sql_code.get_code())

        # Display agent response
        container.chat_message("assistant").markdown(response)

    except Exception as e:
        error_msg = f"System Error: {str(e)}"
        st.error(error_msg)
        st.session_state.messages.append({"role": "system", "content": error_msg})


def render_sidebar():
    """Right-hand sidebar components"""
    with st.container():
        st.title("Analytics Workspace")

        with st.expander("Example Queries", expanded=True):
            st.markdown(
                """
            **Basic Usage**
            - Database schema exploration
            - Field definitions and relationships
            - SOC-related metrics analysis
            
            **Advanced Analysis**
            1. Vehicle mileage statistics
            2. Weekly charging patterns
            3. Fast vs slow charge comparisons
            """
            )

        st.subheader("Query Results")
        st.dataframe(
            st.session_state.get("current_df", pd.DataFrame()),
            use_container_width=True,
            height=300,
        )

        st.subheader("Generated SQL")
        st.code(mem_sql_code.get_code() or INITIAL_SQL, language="sql")

        st.subheader("System Logs")
        st.code(Path(logger_filepath).read_text(), language="log")


def apply_custom_styles():
    """Inject custom CSS styles"""
    st.markdown(
        f"""
    <style>
        /* Main container sizing */
        .stApp {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        /* Chat interface enhancements */
        .stChatInput {{
            bottom: 20px;
            background: rgba(245, 245, 245, 0.9);
        }}
        
        /* Responsive data tables */
        .stDataFrame {{
            margin: 1rem 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def main():
    """Main application flow"""
    init_session_state()
    apply_custom_styles()
    agent = init_agent()

    # Main layout
    main_col, sidebar_col = st.columns([3, 2], gap="large")

    with main_col:
        render_chat_interface(agent)

    with sidebar_col:
        render_sidebar()


if __name__ == "__main__":
    main()
