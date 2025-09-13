from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from config.settings import settings
from tools.chart_tools import ChartTools  # 导入图表工具
from typing import List, Dict, Any, Union

# ... (顶部导入不变) ...
from tools.chart_tools import ChartTools
from langchain.tools import tool # 导入 tool 装饰器

# 实例化 ChartTools
_chart_tools_instance = ChartTools()

@tool("生成股票K线图")
def generate_candlestick_chart_tool(data: List[Dict[str, Any]], title: str = "股票K线图") -> str:
    """根据提供的股票数据生成K线图，并返回其描述或Base64编码图片。
    输入为包含'日期', '开盘价', '最高价', '最低价', '收盘价', '成交量'的字典列表。"""
    return _chart_tools_instance.generate_candlestick_chart(data, title)

class AnalysisAgent:
    def __init__(self):
        self.llm = ChatTongyi(
            model=settings.default_model,
            dashscope_api_key=settings.qwen_api_key,
            temperature=settings.temperature
        )
        # ✅ 修复：直接使用装饰器后的工具函数列表
        self.tools = [generate_candlestick_chart_tool]
        # ... (其余不变) ...
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的金融分析师，根据提供的数据和用户请求，生成详细、客观的分析报告。如果需要图表，请使用工具生成。"),
            ("placeholder", "{chat_history}"),
            ("human", "请根据以下数据进行分析：\n数据：{data_context}\n用户请求：{input}"),
        ])

    def run(
        self,
        input_data: str,
        data_context: Union[str, Dict[str, Any]],
        chat_history: List[BaseMessage] = None
    ) -> str:
        """执行数据分析任务，返回分析结果。"""
        print(f"\n--- Analysis Agent: 接收到请求 ---")
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
                chat_history=history_for_agent
            )

            llm_with_tools = self.llm.bind_tools(self.tools)
            response = llm_with_tools.invoke(messages)

            if response.tool_calls:
                tool_output = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    if tool_name == "生成股票K线图":
                        chart_result = self.chart_tools.generate_candlestick_chart(
                            tool_args.get("data", data_context.get("price_data", [])),
                            tool_args.get("title", "股票K线图")
                        )
                        tool_output.append(f"工具调用结果 ({tool_name}): {chart_result}")
                    else:
                        tool_output.append(f"未知工具: {tool_name}")

                final_messages = messages + [
                    AIMessage(content=response.content, tool_calls=response.tool_calls),
                    HumanMessage(content="\n".join(tool_output))
                ]
                final_response = self.llm.invoke(final_messages)
                return final_response.content + "\n" + "\n".join(tool_output)

            print(f"--- Analysis Agent: 完成任务 ---")
            return response.content
        except Exception as e:
            print(f"[错误] Analysis Agent 执行失败: {e}")
            return f"分析失败: {e}"
