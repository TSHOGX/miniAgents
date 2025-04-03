import streamlit as st
import sys
import os
import pandas as pd
import json
import datetime
import time
import hashlib
from typing import Dict, List, Optional, Any

# 确保可以导入app模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents import SQLAgent, DbInfoAgent, SimpleChatter
from app.prompts.db_info import DB_INFO


def get_user_dir(user_id):
    """获取用户目录"""
    # 创建用户目录（如果不存在）
    user_hash = hashlib.md5(user_id.encode()).hexdigest()
    user_dir = f"users/{user_hash}"
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir


def save_chat_history(chat_history, agent_type, user_id):
    """保存特定用户的聊天历史到文件"""
    user_dir = get_user_dir(user_id)

    # 创建文件名（使用时间戳避免覆盖）
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_dir}/chat_history_{agent_type}_{timestamp}.json"

    # 准备保存的数据
    save_data = {
        "timestamp": timestamp,
        "agent_type": agent_type,
        "history": chat_history,
    }

    # 保存到文件
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    return filename


def load_chat_logs(user_id):
    """加载特定用户的所有聊天记录文件"""
    user_dir = get_user_dir(user_id)

    log_files = []
    if not os.path.exists(user_dir):
        return log_files

    for filename in os.listdir(user_dir):
        if filename.startswith("chat_history_") and filename.endswith(".json"):
            file_path = os.path.join(user_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 添加文件路径以便后续操作
                    data["file_path"] = file_path
                    log_files.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    # 按时间戳排序，最新的在前
    log_files.sort(key=lambda x: x["timestamp"], reverse=True)
    return log_files


def login_page():
    """显示登录页面"""
    st.title("欢迎使用BatteryGPT智能对话系统")

    st.write("请输入您的唯一ID进行登录")

    user_id = st.text_input("用户ID", key="login_user_id")

    if st.button("登录"):
        if user_id.strip():
            st.session_state.user_id = user_id
            st.session_state.is_logged_in = True
            st.success(f"欢迎, {user_id}!")

            # 初始化用户的会话状态
            initialize_session_state()

            # 加载用户的聊天记录
            st.session_state.saved_chats = load_chat_logs(user_id)

            time.sleep(1)
            st.rerun()
        else:
            st.error("请输入有效的用户ID")

    # 可选：添加一个访客登录选项
    if st.button("以访客身份登录"):
        guest_id = f"guest_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        st.session_state.user_id = guest_id
        st.session_state.is_logged_in = True
        st.success(f"以访客身份登录: {guest_id}")

        # 初始化访客的会话状态
        initialize_session_state()

        time.sleep(1)
        st.rerun()


def initialize_session_state():
    """初始化会话状态"""
    if "sql_agent" not in st.session_state:
        st.session_state.sql_agent = SQLAgent(
            table_schema=DB_INFO["TABLE_SCHEMA"],
            db_info=DB_INFO["DB_INFO"],
            helper_info=DB_INFO["HELPER_INFO"],
        )

    if "db_info_agent" not in st.session_state:
        st.session_state.db_info_agent = DbInfoAgent()

    if "simple_chatter" not in st.session_state:
        st.session_state.simple_chatter = SimpleChatter()

    if "current_agent" not in st.session_state:
        st.session_state.current_agent = st.session_state.simple_chatter

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "saved_chats" not in st.session_state:
        st.session_state.saved_chats = []


def display_chat_history():
    """显示聊天历史"""
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            with st.chat_message("user", avatar="🥳"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(message["content"])


def display_agent_state():
    """显示当前Agent的状态"""
    current_agent = st.session_state.current_agent
    agent_type = get_agent_type()

    with st.expander(f"当前Agent状态: {agent_type}", expanded=False):
        # st.json(current_agent.memory.to_dict_list())
        st.code(current_agent.memory.curr_sql(), language="sql")
        st.dataframe(current_agent.memory.curr_df())


def get_agent_type():
    """获取当前Agent的类型"""
    current_agent = st.session_state.current_agent
    if current_agent == st.session_state.sql_agent:
        return "SQL Agent"
    elif current_agent == st.session_state.db_info_agent:
        return "DB Info Agent"
    else:
        return "Simple Chatter"


def switch_agent(agent_name):
    """切换当前使用的Agent"""
    if agent_name == "sql":
        st.session_state.current_agent = st.session_state.sql_agent
        st.session_state.current_agent.memory.clear()
        response = "SQL Agent 已准备就绪"
    elif agent_name == "db":
        st.session_state.current_agent = st.session_state.db_info_agent
        st.session_state.current_agent.memory.clear()
        response = "DB Info Agent 已准备就绪"
    elif agent_name == "new":
        st.session_state.current_agent = st.session_state.simple_chatter
        st.session_state.current_agent.memory.clear()
        response = "Simple Chatter 已准备就绪"
    else:
        return None

    # 添加系统消息到聊天历史
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    return response


def process_input(user_input):
    """处理用户输入"""
    # 添加用户消息到聊天历史
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 命令处理
    if user_input == "sql":
        response = switch_agent("sql")
    elif user_input == "db":
        response = switch_agent("db")
    elif user_input == "new":
        response = switch_agent("new")
    else:
        # 使用当前Agent处理问题
        response = st.session_state.current_agent.run(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    return response


def display_chat_logs():
    """显示并管理已保存的聊天记录"""
    st.header("保存的聊天记录")

    if not st.session_state.saved_chats:
        st.info("没有保存的聊天记录")
        return

    for idx, chat_log in enumerate(st.session_state.saved_chats):
        # 显示聊天记录概要
        with st.expander(f"{chat_log['agent_type']} - {chat_log['timestamp']}"):
            # 添加操作按钮
            col1, col2 = st.columns(2)
            with col1:
                if st.button("加载此对话", key=f"load_{idx}"):
                    # 加载此对话到当前会话
                    st.session_state.chat_history = chat_log["history"].copy()

                    # 确定并设置对应的Agent
                    if chat_log["agent_type"] == "SQL Agent":
                        st.session_state.current_agent = st.session_state.sql_agent
                    elif chat_log["agent_type"] == "DB Info Agent":
                        st.session_state.current_agent = st.session_state.db_info_agent
                    else:
                        st.session_state.current_agent = st.session_state.simple_chatter

                    st.success("已加载")
                    time.sleep(0.5)
                    st.rerun()

            with col2:
                if st.button("删除此对话", key=f"delete_{idx}"):
                    # 删除文件
                    try:
                        os.remove(chat_log["file_path"])
                        st.session_state.saved_chats.pop(idx)
                        st.success("已删除")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"删除失败: {e}")

            # 显示对话内容
            for message in chat_log["history"]:
                if message["role"] == "user":
                    st.markdown(f"**🥳 用户**: {message['content']}")
                else:
                    st.markdown(f"**🤖 助手**: {message['content']}")


def main_app():
    """主应用界面"""

    # 侧边栏 - Agent选择和历史记录
    with st.sidebar:
        st.write(f"当前用户: **{st.session_state.user_id}**")
        st.divider()

        st.header("选择 Agent")

        if st.button("SQL Agent"):
            switch_agent("sql")
            st.rerun()

        if st.button("DB Info Agent"):
            switch_agent("db")
            st.rerun()

        if st.button("Simple Chatter"):
            switch_agent("new")
            st.rerun()

        st.write(f"当前 Agent: **{get_agent_type()}**")

        st.divider()

        if st.button("清空并保存聊天历史"):
            if st.session_state.chat_history:
                # 保存当前对话
                saved_file = save_chat_history(
                    st.session_state.chat_history,
                    get_agent_type(),
                    st.session_state.user_id,
                )

                # 清空当前对话
                st.session_state.chat_history = []
                st.session_state.current_agent.memory.clear()

                # 重新加载已保存聊天记录列表
                st.session_state.saved_chats = load_chat_logs(st.session_state.user_id)

                st.success(f"聊天记录已保存")
                time.sleep(1)
                st.rerun()
            else:
                st.info("当前没有聊天记录可保存")

        # 添加单独的保存按钮
        if st.button("仅保存当前对话"):
            if st.session_state.chat_history:
                saved_file = save_chat_history(
                    st.session_state.chat_history,
                    get_agent_type(),
                    st.session_state.user_id,
                )
                st.session_state.saved_chats = load_chat_logs(st.session_state.user_id)
                st.success(f"聊天记录已保存")
                time.sleep(1)
                st.rerun()
            else:
                st.info("当前没有聊天记录可保存")

        # 添加注销按钮
        if st.button("注销"):
            # 清理会话状态
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.session_state.is_logged_in = False
            st.rerun()

        # 历史记录区域
        st.divider()
        display_chat_logs()

    # 主聊天区域
    st.header("当前对话")

    # 显示聊天历史
    display_chat_history()

    # 显示Agent状态
    display_agent_state()

    # 用户输入
    user_input = st.chat_input("请输入您的问题...")
    if user_input:
        process_input(user_input)
        st.rerun()


def main():
    """主函数，处理页面导航逻辑"""
    # 创建必要的目录
    if not os.path.exists("users"):
        os.makedirs("users")

    # 检查是否已登录
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False

    # 根据登录状态显示不同页面
    if not st.session_state.is_logged_in:
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    main()
