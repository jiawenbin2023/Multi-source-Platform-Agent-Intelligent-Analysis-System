import tushare as ts
import requests
from bs4 import BeautifulSoup
from config.settings import settings
import pandas as pd
import re


class StockTools:

    def __init__(self):
        self.tushare_token = settings.tushare_token
        self.pro = None

        if self.tushare_token:
            try:
                ts.set_token(self.tushare_token)
                self.pro = ts.pro_api()
                print("[DEBUG StockTools] TuShare Pro API initialized successfully.")
            except Exception as e:
                print(f"[ERROR StockTools] TuShare Pro API initialization failed: {e}. "
                      f"Will only use fallback data sources.")
                self.pro = None
        else:
            print("[WARNING StockTools] TUSHARE_TOKEN not configured. "
                  "Will only use fallback data sources.")
            self.pro = None

    def get_stock_price_internal(self, ts_code: str = "600519.SH") -> dict:
        """
        获取股票最近5天行情，优先TuShare，失败回退新浪财经。
        这是一个内部方法。
        """
        if self.pro:
            try:
                df = self.pro.daily(ts_code=ts_code, limit=5)
                if df is None or df.empty:
                    raise Exception("TuShare无数据或无权限")
                print(f"[DEBUG StockTools] Successfully got stock price from TuShare for {ts_code}.")
                return df.to_dict(orient="records")
            except Exception as e:
                print(f"[WARNING StockTools] TuShare getting stock price failed: {e}. "
                      f"Trying fallback Sina/Tencent.")
        else:
            print(f"[WARNING StockTools] TuShare Pro API not available. "
                  f"Trying fallback Sina/Tencent for {ts_code} price.")

        return self._get_price_from_sina(ts_code)

    def get_company_info_internal(self, ts_code: str = "600519.SH") -> dict:
        """
        获取公司信息，优先TuShare，失败回退新浪财经。
        这是一个内部方法。
        """
        if self.pro:
            try:
                df = self.pro.stock_company(ts_code=ts_code)
                if df is None or df.empty:
                    raise Exception("TuShare无数据或无权限")
                print(f"[DEBUG StockTools] Successfully got company info from TuShare for {ts_code}.")
                return df.to_dict(orient="records")
            except Exception as e:
                print(f"[WARNING StockTools] TuShare getting company info failed: {e}. Trying fallback Sina.")
        else:
            print(f"[WARNING StockTools] TuShare Pro API not available. Trying fallback Sina for {ts_code} info.")

        return self._get_info_from_sina_html(ts_code)

    def _get_price_from_sina(self, ts_code):
        """从腾讯财经抓取行情"""
        try:
            code = self._code_for_sina(ts_code)
            url = f"https://qt.gtimg.cn/q={code}"
            res = requests.get(url, timeout=5)
            res.encoding = "gbk"
            data = res.text.split('~')

            # 腾讯数据字段较多，检查长度
            if len(data) > 40:
                print(f"[DEBUG StockTools] Successfully got stock price from Sina/Tencent for {ts_code}.")
                return {
                    "name": data[1],
                    "code": ts_code,
                    "current_price": data[3],
                    "last_close": data[4],
                    "open": data[5],
                    "high": data[33] if len(data) > 33 and data[33] else data[3],
                    "low": data[34] if len(data) > 34 and data[34] else data[3],
                    "volume": data[6],
                    "date": data[30]
                }

            print(f"[ERROR StockTools] Sina/Tencent data parsing failed for {ts_code}: Incomplete data. "
                  f"Raw: {res.text[:100]}...")
            return {"error": "新浪/腾讯财经数据解析失败或格式不正确"}

        except Exception as e:
            print(f"[ERROR StockTools] Sina/Tencent getting stock price failed for {ts_code}: {e}")
            return {"error": f"新浪/腾讯财经行情获取失败: {e}"}

    def _get_info_from_sina_html(self, ts_code):
        """爬取新浪财经股票公司概况HTML"""
        try:
            stock_id = ts_code[:6]
            url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{stock_id}.phtml"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            res = requests.get(url, headers=headers, timeout=5)
            res.encoding = "gbk"
            soup = BeautifulSoup(res.text, "html.parser")

            table = soup.find("table", attrs={"class": ["comInfo1", "table2"]})
            if not table:
                print(f"[ERROR StockTools] Sina HTML: Could not find company info table for {ts_code} "
                      f"using 'comInfo1' or 'table2'.")
                title_tag = soup.find("title")
                if title_tag and "公司资料" in title_tag.get_text():
                    company_name_from_title = title_tag.get_text().split('_')[0].strip()
                    return {
                        "error": "未找到详细公司信息表格，但通过标题获取了公司名称。",
                        "公司名称": company_name_from_title,
                        "code": ts_code
                    }
                return {"error": "未找到公司信息表格"}

            result = {}
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) >= 2:
                    key = tds[0].get_text(strip=True).replace('：', '')
                    val = tds[1].get_text(strip=True)
                    result[key] = val
            result["code"] = ts_code

            print(f"[DEBUG StockTools] Successfully got company info from Sina HTML for {ts_code}.")
            return result

        except Exception as e:
            print(f"[ERROR StockTools] Sina HTML getting company info failed for {ts_code}: {e}")
            return {"error": f"新浪财经公司信息获取失败: {e}"}

    def _code_for_sina(self, ts_code):
        """将 TuShare ts_code 转成新浪/腾讯接口用的代码"""
        if ts_code.endswith(".SZ"):
            return "sz" + ts_code[:6]
        elif ts_code.endswith(".SH"):
            return "sh" + ts_code[:6]
        else:
            return ts_code
