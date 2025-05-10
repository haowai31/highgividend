# AKShare 数据接口标准用法（高股息A股项目专用）

## 1. 日K线数据
- 接口：`ak.stock_zh_a_hist`
- 用法示例：
```python
import akshare as ak
df = ak.stock_zh_a_hist(symbol="000858", period="daily", start_date="2024-04-01", end_date="2024-05-01", adjust="qfq")
```
- 主要字段：
    - 日期: date
    - 开盘: open
    - 最高: high
    - 最低: low
    - 收盘: close
    - 成交量: volume
    - 成交额: amount

## 2. 财务摘要数据
- 接口：`ak.stock_a_indicator_lg`
- 用法示例：
```python
import akshare as ak
df = ak.stock_a_indicator_lg(symbol="000858")
```
- 主要字段：
    - 日期: date
    - 市盈率-动态: pe_ttm
    - 市净率: pb_mrq
    - 总市值: market_cap
    - 流通市值: circulating_market_cap

## 3. 分红数据
- 接口：`ak.stock_history_dividend_detail`
- 用法示例：
```python
import akshare as ak
df = ak.stock_history_dividend_detail(symbol="000858")
```
- 主要字段：
    - 公告日期: report_date
    - 除权除息日: ex_dividend_date
    - 每股股利(税前): dividend_per_share_pre_tax

---

> **注意：**
> - symbol 传入时去掉市场前缀（如 SZ000858 → 000858）。
> - 字段名如有变动，请以实际返回为准，必要时在 DataManager 里做 rename。
> - 其他A股相关接口请参考 [AKShare官方文档](https://akshare.akfamily.xyz/tutorial.html)。 