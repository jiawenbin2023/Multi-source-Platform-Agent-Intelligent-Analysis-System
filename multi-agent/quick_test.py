from tools.stock_tools import StockTools

if __name__ == "__main__":
    tools = StockTools()
    print("公司信息:", tools.get_company_info("000001.SZ"))
    print("行情数据:", tools.get_stock_price("000001.SZ"))
