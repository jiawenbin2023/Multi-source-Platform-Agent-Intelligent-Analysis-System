import pandas as pd
import mplfinance as mpf
import io
import base64
from langchain.tools import tool
from typing import List, Dict, Any


class ChartTools:
    @tool("生成股票K线图")
    def generate_candlestick_chart(self, data: List[Dict[str, Any]], title: str = "股票K线图") -> str:
        """根据提供的股票数据生成K线图，并返回其描述或Base64编码图片（如果环境支持）。
        输入为包含'日期', '开盘价', '最高价', '最低价', '收盘价', '成交量'的字典列表。
        返回图表描述或Base64编码的图片字符串。
        """
        if not data:
            return "没有足够的历史数据来生成K线图。"

        df = pd.DataFrame(data)
        # 假设数据中包含 'trade_date', 'open', 'high', 'low', 'close', 'vol'
        # 需要根据实际TuShare/新浪财经返回的字段名进行调整
        df.rename(columns={
            'trade_date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume'
        }, inplace=True)

        # 检查是否所有必要的列都存在
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            # 尝试从新浪/腾讯的简单数据中提取
            if 'date' in df.columns and 'open' in df.columns and 'current_price' in df.columns:
                # 这段逻辑需要根据实际传入的数据结构来编写
                # 比如将新浪的单日数据转换为日线数据
                return "数据格式不完整，无法生成K线图。需要历史日线数据。"
            return "数据格式不完整，无法生成K线图。"

        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        # 确保数据按日期排序
        df.sort_index(inplace=True)

        # 检查是否有足够数据
        if len(df) < 2:
            return "数据不足，无法生成K线图。"

        # 生成图表到内存
        try:
            buf = io.BytesIO()
            mc = mpf.make_marketcolors(up='red', down='green', inherit=True)
            s = mpf.make_mpf_style(marketcolors=mc, gridcolor='gray', figcolor='white', y_on_right=False)

            mpf.plot(df, type='candle', style=s, title=title,
                     ylabel='价格', ylabel_lower='成交量',
                     volume=True, savefig=buf, closefig=True)

            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            return f"图表已生成（Base64编码），标题为：{title}。请在支持Base64图片的环境中渲染。"
        except Exception as e:
            return f"生成K线图失败: {e}"

    # @tool("生成简单的折线图")
    # def generate_line_chart(self, data: List[Dict[str, Any]], x_col: str, y_col: str, title: str = "折线图") -> str:
    #     """根据数据生成折线图，并返回其描述。
    #     输入为字典列表，指定X轴和Y轴的列名。"""
    #     # 类似K线图，用matplotlib生成，并返回描述或Base64
    #     return f"生成了关于 {x_col} 和 {y_col} 的折线图，标题为 {title}。"

