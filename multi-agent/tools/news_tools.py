import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Union


class NewsTools:

    def get_company_news(self, company_name: str) -> Union[List[Dict[str, str]], Dict[str, str]]:
        """
        从新浪财经或东方财富抓取与公司相关的新闻。
        输入为公司名称，例如 '贵州茅台'。
        返回包含新闻标题、链接、发布日期等信息的列表。
        """
        try:
            news_items = []

            # 尝试从新浪新闻搜索页面获取
            search_url_generic = f"https://search.sina.com.cn/?q={company_name} 股票&c=news&by=media"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36)"
            }
            res_generic = requests.get(search_url_generic, headers=headers, timeout=5)
            res_generic.encoding = "utf-8"
            soup_generic = BeautifulSoup(res_generic.text, "html.parser")

            for item in soup_generic.select("div.box-result > div.r-info"):
                title_tag = item.select_one("h2 > a")
                date_source_tag = item.select_one("span.fg-c-a")
                if title_tag and date_source_tag:
                    date_text = date_source_tag.get_text(strip=True)
                    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', date_text)
                    date_str = match.group(0) if match else "未知日期"

                    news_items.append({
                        "title": title_tag.get_text(strip=True),
                        "link": title_tag.get("href"),
                        "date": date_str
                    })

                if len(news_items) >= 5:
                    break

            if not news_items:
                print(f"[ERROR NewsTools] No news found for '{company_name}' after general search.")
                return {"error": f"未找到 '{company_name}' 相关新闻"}

            print(f"[DEBUG NewsTools] Successfully retrieved {len(news_items)} news items for '{company_name}'.")
            return news_items

        except Exception as e:
            print(f"[ERROR NewsTools] Getting company news failed for '{company_name}': {e}")
            return {"error": f"获取公司新闻失败: {e}"}
