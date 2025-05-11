# A股辅助决策工具

一个基于Python的A股辅助决策工具，实现策略选股、历史回溯、数据管理和结果输出。

## 功能特点

- 自动获取和更新股票数据（日K线、财务数据、分红数据）
- 支持多种选股策略
- 提供安全分计算
- 灵活的命令行接口
- 完整的日志记录

## 安装步骤

1. 克隆仓库：
```bash
git clone [repository_url]
cd highgividend
```

2. 创建并激活虚拟环境：
```bash
source .venv/bin/activate
```

3. 安装依赖：
```bash
uv pip install -r requirements.txt
```

## 使用方法

### 1. 初始化配置

首次使用需要初始化配置文件：
```bash
python main.py init-config
```
这将创建默认的 `config.json` 和 `stock_pool.json` 文件。

### 2. 更新数据

更新单个股票的数据：
```bash
python main.py update-data --stock SZ000858
```

更新特定类型的数据：
```bash
python main.py update-data --stock SZ000858 --type kline,financial,dividend
```

更新所有股票池中的数据：
```bash
python main.py update-data --all-pools
```

### 3. 选股扫描

扫描默认股票池：
```bash
python main.py scan
```

扫描特定股票池：
```bash
python main.py scan --pool my_watchlist
```

使用特定策略扫描：
```bash
python main.py scan --strategy strategy_1a_daily_bollinger_dividend
```

## 项目结构

```
highgividend/
├── src/
│   ├── data/
│   │   ├── data_manager.py    # 数据管理模块
│   │   ├── db_handler.py      # 数据库处理模块
│   │   └── akshare_rules.md   # akshare接口规则
│   ├── strategies/            # 策略模块
│   └── utils/
│       └── logger.py          # 日志工具
├── tests/                     # 测试用例
├── config.json               # 配置文件
├── stock_pool.json          # 股票池配置
├── requirements.txt         # 依赖包列表
└── main.py                 # 主程序入口
```

## 配置说明

### config.json
- 数据源配置
- 数据库路径
- 日志配置
- 策略参数
- 安全分权重

### stock_pool.json
- 默认股票池
- 自定义股票池

## 开发说明

### 环境要求
- Python 3.9+
- 使用 `uv` 进行Python版本和依赖包管理

### 开发工具
- 使用 `uv venv` 创建虚拟环境
- 使用 `uv pip install` 安装依赖

### 代码风格
- 遵循 PEP 8
- 使用类型注解
- 添加详细的文档字符串

## 注意事项

1. 所有Python相关命令必须在激活虚拟环境后执行
2. 确保网络连接正常以获取实时数据
3. 定期备份数据库文件

## 许可证

[许可证类型]

## 贡献指南

[贡献指南内容]
