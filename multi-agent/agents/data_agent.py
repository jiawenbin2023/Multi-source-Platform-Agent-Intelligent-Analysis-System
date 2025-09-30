from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from config.settings import settings
from tools.stock_tools import StockTools
from tools.news_tools import NewsTools
from langchain.tools import tool
from typing import List, Dict, Any, Union
import json

_stock_tools_instance = StockTools()
_news_tools_instance = NewsTools()


@tool("获取股票价格")
def get_stock_price_tool(ts_code: str = "600519.SH") -> dict:
    """获取指定股票代码最近5天的股票行情"""
    return _stock_tools_instance.get_stock_price_internal(ts_code)


@tool("获取公司信息")
def get_company_info_tool(ts_code: str = "600519.SH") -> dict:
    """获取指定股票代码的上市公司基本信息"""
    return _stock_tools_instance.get_company_info_internal(ts_code)


@tool("获取公司新闻")
def get_company_news_tool(company_name: str) -> List[Dict[str, str]]:
    """获取公司相关新闻"""
    return _news_tools_instance.get_company_news(company_name)


class DataAgent:

    def __init__(self):
        self.llm = ChatTongyi(
            model=settings.default_model,
            dashscope_api_key=settings.qwen_api_key,
            temperature=settings.temperature
        )

        self.tools = [
            get_stock_price_tool,
            get_company_info_tool,
            get_company_news_tool
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的数据收集助手，擅长使用提供的工具获取股票价格、公司信息和公司新闻。"),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=False)

    def run(self, input_data: str, chat_history: List[BaseMessage] = None) -> Union[str, Dict[str, Any]]:
        print(f"\n--- Data Agent: 接收到请求 ---")
        history_for_agent = []

        if chat_history:
            for msg in chat_history:
                if isinstance(msg, HumanMessage):
                    history_for_agent.append(HumanMessage(content=msg.content))
                elif isinstance(msg, AIMessage):
                    history_for_agent.append(AIMessage(content=msg.content))

        try:
            result = self.executor.invoke({"input": input_data, "chat_history": history_for_agent})
            print(f"--- Data Agent: 完成任务 ---")
            if "output" in result:
                try:
                    return json.loads(result["output"])
                except json.JSONDecodeError:
                    return result["output"]
            return result
        except Exception as e:
            print(f"[错误] Data Agent 执行失败: {e}")
            return {"error": f"数据收集失败: {e}"}
