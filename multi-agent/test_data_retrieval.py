# test_data_retrieval.py
import sys
import os
import json # 导入 json 模块
from pprint import pprint # 用于更美观地打印结果

# 确保能找到项目根目录下的模块
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 导入所有需要的模块
from config.settings import settings
from tools.stock_tools import StockTools
# 从 data_agent 导入封装好的工具函数，而不是直接导入 DataAgent
from agents.data_agent import get_stock_price_tool, get_company_info_tool, get_company_news_tool
from agents.data_agent import DataAgent # 用于测试 DataAgent 实例
from main import run_agent_workflow, short_term_memory # 从 main 模块导入 short_term_memory


print("\n" + "="*80)
print("             🚀 开始执行数据链路测试脚本 🚀")
print("="*80)

print("\n--- Step 1: Initialize StockTools and check TuShare status ---")
stock_tools_instance = StockTools()
print(f"TuShare Pro API status: {'Initialized' if stock_tools_instance.pro else 'Failed/Not Configured (check TUSHARE_TOKEN in .env)'}")
print("-" * 50)


print("\n--- Step 2: Directly call StockTools internal methods (bypassing @tool decorator) ---")
ts_code_maotai = "600519.SH"
ts_code_pingan = "000001.SZ"
company_name_maotai = "贵州茅台"

print(f"\nAttempting to get company info for {ts_code_maotai} (贵州茅台) via internal method:")
company_info_maotai = stock_tools_instance.get_company_info_internal(ts_code_maotai)
print("Result:")
pprint(company_info_maotai)
if isinstance(company_info_maotai, dict) and "error" in company_info_maotai:
    print(f"!! ERROR in get_company_info_internal: {company_info_maotai['error']}")
else:
    print("✓ Successfully retrieved company info.")

print(f"\nAttempting to get stock price for {ts_code_maotai} (贵州茅台) via internal method:")
stock_price_maotai = stock_tools_instance.get_stock_price_internal(ts_code_maotai)
print("Result:")
pprint(stock_price_maotai)
if isinstance(stock_price_maotai, dict) and "error" in stock_price_maotai:
    print(f"!! ERROR in get_stock_price_internal: {stock_price_maotai['error']}")
else:
    print("✓ Successfully retrieved stock price.")

print(f"\nAttempting to get company news for {company_name_maotai} via @tool function:")
company_news_maotai = get_company_news_tool(company_name_maotai)
print("Result:")
pprint(company_news_maotai)
if isinstance(company_news_maotai, dict) and "error" in company_news_maotai:
    print(f"!! ERROR in get_company_news_tool: {company_news_maotai['error']}")
else:
    print("✓ Successfully retrieved company news.")
print("-" * 50)


print("\n--- Step 3: Test DataAgent's tool calls (simulating LangChain execution) ---")
data_agent_instance = DataAgent()
# 注意：DataAgent 内部会通过 LLM 决定调用哪些工具，并对结果进行总结
test_user_input_data_agent = f"获取 {ts_code_maotai} (贵州茅台) 的价格、公司信息和新闻"

print(f"\nRunning DataAgent with input: '{test_user_input_data_agent}'")
data_agent_result = data_agent_instance.run(test_user_input_data_agent)
print("DataAgent raw result:")
pprint(data_agent_result)

if isinstance(data_agent_result, dict) and "output" in data_agent_result:
    print(f"DataAgent output (LLM summary): {data_agent_result['output']}")
    # LLM的总结通常不是纯JSON，所以这里不强制解析
    if "error" in data_agent_result['output'].lower() or "无法获取" in data_agent_result['output'].lower():
        print("!! DataAgent's LLM summary indicates an error or inability to retrieve data.")
    else:
        print("✓ DataAgent returned an LLM summary (hopefully with data).")
elif isinstance(data_agent_result, dict) and "error" in data_agent_result:
    print(f"!! DataAgent returned an error: {data_agent_result['error']}")
else:
    print(f"✓ DataAgent returned direct data (if LLM decided not to summarize): {data_agent_result}")
print("-" * 50)


print("\n--- Step 4: Full LangGraph run simulation (for specific analysis) ---")
# 清空记忆，确保新测试干净
short_term_memory.clear()

print(f"\nRunning full LangGraph workflow for '分析一下贵州茅台的投资价值':")
langgraph_analysis_query = "分析一下贵州茅台的投资价值"
langgraph_result_analysis = run_agent_workflow(langgraph_analysis_query)
print(f"\nLangGraph Workflow Final Result (Analysis Query):")
pprint(langgraph_result_analysis)
if "error" in str(langgraph_result_analysis).lower() or "无法进行分析" in str(langgraph_result_analysis).lower():
    print("!! LangGraph workflow analysis failed (likely due to missing data or LLM's own analysis limit).")
else:
    print("✓ LangGraph workflow successfully performed analysis.")

print("\n" + "="*80)
print("             ✅ 数据链路测试结束 ✅")
print("="*80)
