import os
import re
from typing import TypedDict, List, Dict, Any, Union
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from memory.short_memory import ShortTermMemory


# ========= 导入其他模块 =========
from agents.router_agent import RouterAgent
from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.report_agent import ReportAgent
from config.settings import settings


# 定义 LangGraph 的状态
class AgentState(TypedDict):
    user_input: str
    chat_history: List[BaseMessage]
    data_context: Union[str, Dict[str, Any], None]
    analysis_result: Union[str, None]
    report_content: Union[str, None]
    current_agent: str
    route: str
    final_goal: str


# 实例化 Agents 和 记忆
router_agent = RouterAgent()
data_agent = DataAgent()
analysis_agent = AnalysisAgent()
report_agent = ReportAgent()
short_term_memory = ShortTermMemory()


# ======== 定义 LangGraph 节点函数 ========

def call_router(state: AgentState):
    print("----- 进入 Router Node -----")
    route = router_agent.route_request(state["user_input"], state["chat_history"])
    return {"current_agent": "router", "route": route, "final_goal": route}


def call_data_agent(state: AgentState):
    print("----- 进入 Data Agent Node -----")
    result = data_agent.run(state["user_input"], state["chat_history"])
    return {"data_context": result, "current_agent": "data_retrieval"}


def call_analysis_agent(state: AgentState):
    print("----- 进入 Analysis Agent Node -----")
    data_context = state.get("data_context", "没有可用的数据。")
    result = analysis_agent.run(state["user_input"], data_context, state["chat_history"])
    # 将分析结果也映射到 report_content，以便最终统一提取
    return {"analysis_result": result, "report_content": result, "current_agent": "analysis"}


def call_report_agent(state: AgentState):
    print("----- 进入 Report Agent Node -----")
    data_context = state.get("data_context", "没有可用的数据。")
    analysis_result = state.get("analysis_result", "没有可用的分析结果。")
    result = report_agent.run(state["user_input"], data_context, analysis_result, state["chat_history"])
    return {"report_content": result, "current_agent": "report_generation"}


def call_general_response(state: AgentState):
    print("----- 进入 General Response Node -----")
    # 将通用响应也映射到 report_content
    return {"report_content": "抱歉，我无法理解您的请求或执行特定任务。", "current_agent": "general_response"}


# ======== 定义 LangGraph 路由决策函数 ========

def router_decision_logic(state: AgentState) -> str:
    print(f"----- Router Decision Logic: {state.get('route')} -----")
    initial_route = state.get("route", "general_response")
    user_input = state["user_input"]

    # 提取可能的股票名称或代码 (用于判断是否需要数据)
    mentioned_stock_name = ""
    for name in ["贵州茅台", "平安银行", "中国平安", "五粮液"]:
        if name.lower() in user_input.lower():
            mentioned_stock_name = name
            break

    stock_code_pattern = re.compile(r'\b(?:[0-9]{6})\b')
    has_stock_code = stock_code_pattern.search(user_input)

    # 如果初始路由是 analysis 或 report_generation，并且有股票相关关键词，就强制先去 data_retrieval
    if initial_route in ["analysis", "report_generation"] and (mentioned_stock_name or has_stock_code):
        print(
            f"[DEBUG MainRouter] Initial route is {initial_route} for stock-related query. FORCING to data_retrieval first.")
        return "data_retrieval"

    # 否则，按照 LLM/规则给出的初始路由走
    print(f"[DEBUG MainRouter] Proceeding with initial route: {initial_route}.")
    return initial_route


def analysis_decision_logic(state: AgentState) -> str:
    print(f"----- Analysis Decision Logic: Final Goal is {state.get('final_goal')} -----")
    if state.get("final_goal") == "report_generation":
        return "report_generation"
    return END


# 构建 LangGraph
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("router", call_router)
workflow.add_node("data_retrieval", call_data_agent)
workflow.add_node("analysis", call_analysis_agent)
workflow.add_node("report_generation", call_report_agent)
workflow.add_node("general_response", call_general_response)

# 设置入口点
workflow.set_entry_point("router")

# 路由器根据决策转发
workflow.add_conditional_edges(
    "router",
    router_decision_logic,
    {
        "data_retrieval": "data_retrieval",
        "analysis": "analysis",
        "report_generation": "report_generation",
        "general_response": "general_response",
    },
)

# 数据获取后，默认进入分析
workflow.add_edge("data_retrieval", "analysis")

# 分析节点后的条件分支，根据 final_goal 决定是结束还是去生成报告
workflow.add_conditional_edges(
    "analysis",
    analysis_decision_logic,
    {
        "report_generation": "report_generation",
        END: END,
    }
)

# 报告生成或通用响应后结束
workflow.add_edge("report_generation", END)
workflow.add_edge("general_response", END)

# 编译图
app = workflow.compile()


def run_agent_workflow(user_query: str):
    # 更新短期记忆
    short_term_memory.add_message(HumanMessage(content=user_query))
    current_chat_history = short_term_memory.get_messages()

    # 初始状态
    initial_state = AgentState(
        user_input=user_query,
        chat_history=current_chat_history,
        data_context=None,
        analysis_result=None,
        report_content=None,
        current_agent="start",
        route="",
        final_goal=""
    )
    # 运行图
    final_state = None
    for s in app.stream(initial_state):
        final_state = s
        current_node_key = list(s.keys())[0] if s else "Unknown"
        print(f"--- 当前节点: {current_node_key} ---")

    # 智能地提取最终输出，根据 final_goal 优先级
    final_output = "系统未能生成预期结果。"
    if final_state:
        resolved_final_state = final_state.get(END) if END in final_state else None
        if not resolved_final_state:
            last_node_key = list(final_state.keys())[-1]
            resolved_final_state = final_state[last_node_key]

        if resolved_final_state:
            final_goal = resolved_final_state.get("final_goal")

            # 优先级：报告 -> 分析 -> 数据 -> 兜底
            if final_goal == "report_generation" and resolved_final_state.get("report_content"):
                final_output = resolved_final_state["report_content"]
            elif final_goal == "analysis" and resolved_final_state.get("report_content"):
                final_output = resolved_final_state["report_content"]
            elif final_goal == "data_retrieval" and resolved_final_state.get("data_context"):
                final_output = str(resolved_final_state["data_context"])
            elif resolved_final_state.get("report_content"):
                final_output = resolved_final_state["report_content"]
            elif resolved_final_state.get("analysis_result"):
                final_output = resolved_final_state["analysis_result"]
            elif resolved_final_state.get("data_context"):
                final_output = str(resolved_final_state["data_context"])
            else:
                final_output = "未能获取到预期结果，请检查AgentState内容。"
        else:
            final_output = "系统未返回任何状态，可能在启动时发生错误。"
    else:
        final_output = "系统未返回任何状态，可能在启动时发生错误。"

    # 更新记忆
    short_term_memory.add_message(AIMessage(content=final_output))
    return final_output


if __name__ == "__main__":
    print("金融多智能体系统启动，国内版，基于LangGraph和Qwen。")
    while True:
        user_input = input("\n[你]: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        response = run_agent_workflow(user_input)
        print(f"[AI]: {response}")

