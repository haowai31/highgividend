"""
测试 akshare API 调用 - 尝试所有可能的财务和K线接口
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def test_stock_daily_kline():
    print("\n尝试 stock_zh_a_hist ...")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    try:
        df = ak.stock_zh_a_hist(symbol="000858", period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        print("stock_zh_a_hist 列名:", df.columns.tolist())
        print(df.head())
    except Exception as e:
        print("stock_zh_a_hist 错误:", e)

    print("\n尝试 stock_zh_a_daily ...")
    try:
        df2 = ak.stock_zh_a_daily(symbol="sz000858")
        print("stock_zh_a_daily 列名:", df2.columns.tolist())
        print(df2.head())
    except Exception as e:
        print("stock_zh_a_daily 错误:", e)

def test_stock_financial():
    print("\n尝试 stock_a_indicator_lg ...")
    try:
        df = ak.stock_a_indicator_lg(symbol="000858")
        print("stock_a_indicator_lg 列名:", df.columns.tolist())
        print(df.head())
    except Exception as e:
        print("stock_a_indicator_lg 错误:", e)

    print("\n尝试 stock_a_ttm_lyr ...")
    try:
        df2 = ak.stock_a_ttm_lyr(symbol="000858")
        print("stock_a_ttm_lyr 列名:", df2.columns.tolist())
        print(df2.head())
    except Exception as e:
        print("stock_a_ttm_lyr 错误:", e)

    print("\n尝试 stock_a_gxl_lg ...")
    try:
        df3 = ak.stock_a_gxl_lg(symbol="000858")
        print("stock_a_gxl_lg 列名:", df3.columns.tolist())
        print(df3.head())
    except Exception as e:
        print("stock_a_gxl_lg 错误:", e)

def test_stock_dividend():
    print("\n尝试 stock_history_dividend_detail ...")
    try:
        df = ak.stock_history_dividend_detail(symbol="000858")
        print("stock_history_dividend_detail 列名:", df.columns.tolist())
        print(df.head())
    except Exception as e:
        print("stock_history_dividend_detail 错误:", e)

    print("\n尝试 stock_dividend_cninfo ...")
    try:
        df2 = ak.stock_dividend_cninfo(symbol="000858")
        print("stock_dividend_cninfo 列名:", df2.columns.tolist())
        print(df2.head())
    except Exception as e:
        print("stock_dividend_cninfo 错误:", e)

def main():
    print("测试 akshare API 可用性")
    print("=" * 50)
    test_stock_daily_kline()
    print("-" * 50)
    test_stock_financial()
    print("-" * 50)
    test_stock_dividend()

if __name__ == "__main__":
    main() 