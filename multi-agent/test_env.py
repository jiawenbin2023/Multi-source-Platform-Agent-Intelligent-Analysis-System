# 测试所有关键库是否正确安装
def test_imports():
    try:
        import langgraph
        print("✅ LangGraph:", langgraph.__version__)
    except ImportError as e:
        print("❌ LangGraph 安装失败:", e)

    try:
        import autogen
        print("✅ AutoGen:", autogen.__version__)
    except ImportError as e:
        print("❌ AutoGen 安装失败:", e)

    try:
        import langchain
        print("✅ LangChain:", langchain.__version__)
    except ImportError as e:
        print("❌ LangChain 安装失败:", e)

    try:
        import openai
        print("✅ OpenAI:", openai.__version__)
    except ImportError as e:
        print("❌ OpenAI 安装失败:", e)

    try:
        import yfinance as yf
        print("✅ YFinance:", yf.__version__)
    except ImportError as e:
        print("❌ YFinance 安装失败:", e)

    try:
        import pandas as pd
        print("✅ Pandas:", pd.__version__)
    except ImportError as e:
        print("❌ Pandas 安装失败:", e)

    try:
        import streamlit as st
        print("✅ Streamlit:", st.__version__)
    except ImportError as e:
        print("❌ Streamlit 安装失败:", e)


if __name__ == "__main__":
    print("🔍 检查金融Agent环境依赖...")
    test_imports()
    print("\n🎉 环境检查完成！")
