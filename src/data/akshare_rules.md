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

## 已实现的接口

### 1. 数据获取接口

#### 1.1 日K线数据
- 接口：`ak.stock_zh_a_hist`
- 参数：
  - symbol: 股票代码（如：000858）
  - period: "daily"
  - start_date: 开始日期（YYYYMMDD）
  - end_date: 结束日期（YYYYMMDD）
  - adjust: "qfq"（前复权）
- 返回字段映射：
  - 日期 -> date
  - 开盘 -> open
  - 收盘 -> close
  - 最高 -> high
  - 最低 -> low
  - 成交量 -> volume
  - 成交额 -> amount
  - 振幅 -> amplitude
  - 涨跌幅 -> pct_change
  - 涨跌额 -> change
  - 换手率 -> turnover

#### 1.2 财务摘要数据
- 接口：`ak.stock_a_indicator_lg`
- 参数：
  - symbol: 股票代码（如：000858）
- 返回字段映射：
  - 日期 -> date
  - 市盈率-动态 -> pe_ttm
  - 市净率 -> pb_mrq
  - 总市值 -> market_cap
  - 流通市值 -> circulating_market_cap

#### 1.3 分红数据
- 接口：`ak.stock_history_dividend_detail`
- 参数：
  - symbol: 股票代码（如：000858）
- 返回字段映射：
  - 公告日期 -> report_date
  - 除权除息日 -> ex_dividend_date
  - 每股股利(税前) -> dividend_per_share_pre_tax
  - 股息率 -> dividend_yield

### 2. 命令行接口

#### 2.1 初始化配置
```bash
python main.py init-config
```
- 功能：生成默认的 config.json 和 stock_pool.json 文件
- 配置文件包含：
  - 数据源配置
  - 数据库路径
  - 日志配置
  - 策略参数
  - 安全分权重

#### 2.2 更新数据
```bash
python main.py update-data [--stock STOCK_CODE] [--all-pools] [--type TYPE] [--start-date START_DATE]
```
- 参数：
  - --stock: 指定单个股票代码
  - --all-pools: 更新所有股票池中的股票
  - --type: 指定更新数据类型（kline,financial,dividend）
  - --start-date: 指定历史数据更新的起始日期

#### 2.3 选股扫描
```bash
python main.py scan [--pool POOL_NAME] [--date DATE] [--strategy STRATEGY_NAME]
```
- 参数：
  - --pool: 指定要扫描的股票池（默认：default_pool）
  - --date: 指定扫描日期
  - --strategy: 指定运行特定策略

### 3. 数据库接口

#### 3.1 数据库表结构
- daily_kline: 日K线数据
- weekly_kline: 周K线数据
- monthly_kline: 月K线数据
- dividend_data: 分红数据
- financial_summary: 财务摘要数据
- historical_signals: 历史策略信号
- data_update_log: 数据更新日志

#### 3.2 数据更新日志
- 记录每次数据更新的状态
- 包含表名、股票代码、最后更新日期等信息 