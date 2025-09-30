import sys, os
# 获取 ui/streamlit_app.py 的上一级目录（项目根目录）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from main import run_agent_workflow, short_term_memory # 导入LangGraph运行函数和记忆

st.set_page_config(page_title="金融多智能体分析系统", layout="wide")

st.title("💰 金融多智能体分析系统 (国内版)")
st.caption("基于LangGraph和通义千问，提供股票数据、分析和报告生成。")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示聊天历史
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# 用户输入
if prompt := st.chat_input("输入你的问题，例如：分析一下贵州茅台的投资价值"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.chat_message("user").write(prompt)

    with st.spinner("AI正在思考..."):
        # 调用 LangGraph 运行函数
        response = run_agent_workflow(prompt)
        ai_message = AIMessage(content=response)
        st.session_state.messages.append(ai_message)
        st.chat_message("assistant").write(response)

st.sidebar.title("系统信息")
st.sidebar.write("模型：通义千问 Qwen-turbo")
st.sidebar.write("数据：TuShare (回退新浪财经)")
st.sidebar.write("架构：LangGraph 多智能体协作")

if st.sidebar.button("清除聊天记录"):
    st.session_state.messages = []
    short_term_memory.clear() # 清除后端记忆
    st.experimental_rerun()

