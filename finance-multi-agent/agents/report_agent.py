from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from config.settings import settings
from typing import List, Dict, Any, Union


class ReportAgent:
    def __init__(self):
        self.llm = ChatTongyi(
            model=settings.default_model,
            dashscope_api_key=settings.qwen_api_key,
            temperature=settings.temperature
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的报告生成助手，请根据提供的数据、分析结果和用户请求，生成一份结构清晰、内容详尽的金融报告。"),
            ("placeholder", "{chat_history}"),
            ("human", "请根据以下信息生成一份报告：\n用户请求：{input}\n原始数据：{data_context}\n分析结果：{analysis_result}"),
        ])

    def run(
        self,
        input_data: str,
        data_context: Union[str, Dict[str, Any]],
        analysis_result: str,
        chat_history: List[BaseMessage] = None
    ) -> str:
        """执行报告生成任务，返回最终报告"""
        print(f"\n--- Report Agent: 接收到请求 ---")
        history_for_agent = []
        if chat_history:
            for msg in chat_history:
                if isinstance(msg, HumanMessage):
                    history_for_agent.append(HumanMessage(content=msg.content))
                elif isinstance(msg, AIMessage):
                    history_for_agent.append(AIMessage(content=msg.content))

        if isinstance(data_context, dict):
            data_str = str(data_context)
        else:
            data_str = data_context

        try:
            messages = self.prompt.format_messages(
                input=input_data,
                data_context=data_str,
                analysis_result=analysis_result,
                chat_history=history_for_agent
            )
            response = self.llm.invoke(messages)
            print(f"--- Report Agent: 完成任务 ---")
            return response.content
        except Exception as e:
            print(f"[错误] Report Agent 执行失败: {e}")
            return f"报告生成失败: {e}"
