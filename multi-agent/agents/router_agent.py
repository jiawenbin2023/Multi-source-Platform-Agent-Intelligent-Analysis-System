from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from config.settings import settings
from typing import List


class RouterAgent:
    def __init__(self):
        self.llm = ChatTongyi(
            model=settings.default_model,
            dashscope_api_key=settings.qwen_api_key,
            temperature=settings.temperature
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个智能路由助手，负责将用户请求路由到合适的Agent。请根据用户的问题判断任务类别（data_retrieval/analysis/report_generation/general_response），直接返回类别字符串。"),
            ("human", "用户请求：{input}")
        ])

    def route_request(self, user_input: str, chat_history: List[BaseMessage] = None) -> str:
        """识别用户需求，路由到正确的 Agent"""
        print(f"\n--- Router Agent: 接收到请求 ---")
        history_for_agent = []
        if chat_history:
            for msg in chat_history:
                if isinstance(msg, HumanMessage):
                    history_for_agent.append(HumanMessage(content=msg.content))
                elif isinstance(msg, AIMessage):
                    history_for_agent.append(AIMessage(content=msg.content))

        try:
            response = self.llm.invoke(self.prompt.format_messages(input=user_input))
            route = response.content.strip().lower()

            # 规则加强，覆盖模型结果
            if any(k in user_input for k in ['价格', '行情', '信息', '数据']):
                route = 'data_retrieval'
            elif any(k in user_input for k in ['分析', '建议', '价值']):
                route = 'analysis'
            elif any(k in user_input for k in ['报告', '总结']):
                route = 'report_generation'
            else:
                route = 'general_response'

            print(f"--- Router Agent: 跳转到 {route} ---")
            return route
        except Exception as e:
            print(f"[错误] Router Agent 执行失败: {e}")
            return "general_response"
