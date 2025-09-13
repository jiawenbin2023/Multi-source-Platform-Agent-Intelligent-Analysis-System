# 📈 金融多智能体分析系统

这是一个基于 LangGraph 框架和通义千问（Qwen）大模型的金融多智能体协作系统。旨在通过模拟人类专家团队的工作流程，实现对股票信息的智能获取、深度分析及专业报告生成。该系统集成了数据爬取工具（TuShare / 新浪财经 / 腾讯财经）、图表生成工具、以及强大的语言模型分析能力，为用户提供一站式的金融信息服务。

## ✨ **项目亮点**

*   **多智能体协作**：系统包含路由智能体（Router Agent）、数据获取智能体（Data Agent）、分析智能体（Analysis Agent）和报告生成智能体（Report Agent），各司其职，高效协同。
*   **LangGraph 驱动**：利用 LangGraph 框架构建复杂的工作流，实现智能体之间的动态路由和状态管理，确保任务流程的灵活与健壮。
*   **数据整合能力**：集成 TuShare、新浪财经、腾讯财经等多种数据源，支持获取实时股票价格、公司基本信息、新闻资讯等，并具备数据源回退机制。
*   **深度分析与报告**：分析智能体能够结合用户请求和获取的数据进行深入分析，评估投资价值；报告智能体则能将分析结果结构化为专业报告。
*   **交互式用户界面**：提供基于 Streamlit 的Web界面，支持多轮对话，提升用户体验。
*   **国内化支持**：默认采用通义千问（Qwen）作为核心LLM，并针对国内金融数据源进行优化，适合国内用户。

## 🚀 **功能特性**

*   **智能路由**：根据用户输入自动判断任务类型，将请求分发至最合适的智能体。
*   **实时数据获取**：获取股票（A股）的实时价格、历史行情、公司基本面信息及相关新闻。
*   **投资价值分析**：对特定股票进行多维度分析，提供投资建议。
*   **自动化报告生成**：根据数据和分析结果，自动生成结构清晰、内容专业的金融报告。
*   **图表可视化**：集成 `mplfinance`，可根据数据生成股票K线图（需数据支持）。
*   **短期记忆**：支持多轮对话，理解上下文，提供更连贯的交互体验。

## 🛠️ **技术栈**

*   **核心框架**：Python 3.9+
*   **LLM 框架**：LangChain, LangGraph
*   **大语言模型**：通义千问 (Qwen-turbo / Qwen-plus)
*   **UI 框架**：Streamlit
*   **数据获取**：TuShare, Requests, BeautifulSoup (网页爬虫)
*   **数据处理**：Pandas
*   **图表生成**：`mplfinance`
*   **环境管理**：Conda / Pip
*   **配置管理**：`python-dotenv`

## ⚙️ **环境搭建与运行**

### **1. 克隆项目**

```bash
git clone https://github.com/你的GitHub用户名/你的仓库名.git
cd 你的仓库名


### **2. 创建并激活虚拟环境**

推荐使用 `conda`：

```bash
conda create -n finance-agent python=3.11 -y
conda activate finance-agent
```

或使用 `venv`：

```bash
python -m venv finance-agent
source finance-agent/bin/activate # Linux/macOS
# finance-agent\Scripts\activate # Windows
```

### **3. 安装依赖**

```bash
pip install -r requirements.txt
# 如果遇到安装 mplfinance 报错，可以尝试：
# pip install mplfinance -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**`requirements.txt` 参考内容：**

```
langchain_community
langchain_core
langgraph
streamlit
python-dotenv
tushare
requests
beautifulsoup4
pandas
mplfinance
pydantic_settings
```

### **4. 配置环境变量 `.env`**

在项目根目录下创建 `.env` 文件，并填入你的 API Keys 和配置：

```ini
# .env 文件示例
# 阿里云 DashScope (通义千问) API Key
QWEN_API_KEY=sk-xx
# TuShare 数据接口 Token (免费用户权限有限，但会回退到新浪/腾讯财经)
TUSHARE_TOKEN=xx
# 默认使用的通义千问模型
DEFAULT_MODEL=qwen-turbo
# LLM 生成的温度 (0.0-1.0，越低越确定性)
TEMPERATURE=0.1
```

### **5. 运行项目**

#### **a. CLI 命令行模式 (测试 LangGraph 核心逻辑)**

```bash
python main.py
```

#### **b. Streamlit Web UI 模式 (推荐)**

```bash
streamlit run ui/streamlit_app.py
```

在浏览器中打开显示的 `Local URL` (通常是 `http://localhost:8501`) 即可与系统交互。

## 🤝 **贡献**

欢迎提出 Bug 报告、功能建议或贡献代码。请遵循以下步骤：

1. Fork 本仓库。
2. 创建新的功能分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 创建 Pull Request。

## 📄 **许可证**

本项目采用 MIT 许可证。

------

## 📞 **联系**

如果你有任何问题或建议，欢迎通过 GitHub Issue 提交，或者发送邮件至 1039995947@qq.com。
