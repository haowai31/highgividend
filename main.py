"""
主程序入口
"""
import argparse
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from src.data.data_manager import DataManager
from src.data.db_handler import DatabaseHandler
from src.utils.logger import setup_logger

def load_stock_pool(pool_name: str = "default_pool") -> list:
    """
    加载股票池
    
    Args:
        pool_name: 股票池名称，默认为 default_pool
        
    Returns:
        list: 股票代码列表
    """
    try:
        with open("stock_pool.json", "r", encoding="utf-8") as f:
            pools = json.load(f)
            return pools.get(pool_name, [])
    except Exception as e:
        logger.error(f"加载股票池失败: {str(e)}")
        return []

def init_config():
    """初始化配置文件"""
    # 创建默认的 config.json
    default_config = {
        "data_source": {
            "akshare_max_retries": 3,
            "akshare_retry_delay_seconds": 10,
            "proxies": None
        },
        "database_path": "stock_data.db",
        "log_level": "INFO",
        "log_file_path": "app.log",
        "scan_output_dir": "scan_results",
        "strategies": {
            "strategy_1a_daily_bollinger_dividend": {
                "enabled": True,
                "bollinger_period": 20,
                "bollinger_std_dev": 2.0,
                "bollinger_flat_check_days": 60,
                "bollinger_flat_threshold_percentage": 5.0,
                "min_dynamic_dividend_yield": 3.0
            }
        },
        "safety_score_weights": {
            "pe_percentile": 0.4,
            "pb_percentile": 0.4,
            "dividend_yield_percentile": 0.2
        }
    }
    
    # 创建默认的 stock_pool.json
    default_pool = {
        "default_pool": ["SZ000858"],
        "my_watchlist": ["SZ000858"]
    }
    
    try:
        if not os.path.exists("config.json"):
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            logger.info("已创建默认配置文件 config.json")
            
        if not os.path.exists("stock_pool.json"):
            with open("stock_pool.json", "w", encoding="utf-8") as f:
                json.dump(default_pool, f, indent=4, ensure_ascii=False)
            logger.info("已创建默认股票池文件 stock_pool.json")
    except Exception as e:
        logger.error(f"初始化配置文件失败: {str(e)}")

def update_data(args):
    """更新数据"""
    # 初始化数据库处理器
    db = DatabaseHandler("config.json")
    db.initialize_tables()
    
    # 初始化数据管理器
    dm = DataManager(db)
    
    # 获取当前日期和30天前的日期
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # 确定要更新的股票列表
    if args.all_pools:
        stock_codes = []
        with open("stock_pool.json", "r", encoding="utf-8") as f:
            pools = json.load(f)
            for pool in pools.values():
                stock_codes.extend(pool)
        stock_codes = list(set(stock_codes))  # 去重
    elif args.stock:
        stock_codes = [args.stock]
    else:
        stock_codes = load_stock_pool()
    
    # 确定要更新的数据类型
    data_types = args.type.split(',') if args.type else ['kline', 'financial', 'dividend']
    
    # 更新数据
    for stock_code in stock_codes:
        logger.info(f"更新 {stock_code} 的数据")
        dm.update_single_stock_data(stock_code, data_types)

def scan(args):
    """执行选股扫描"""
    # TODO: 实现选股扫描逻辑
    logger.info("选股扫描功能待实现")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="A股辅助决策工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init-config 命令
    subparsers.add_parser("init-config", help="生成默认配置文件")
    
    # update-data 命令
    update_parser = subparsers.add_parser("update-data", help="更新数据")
    update_parser.add_argument("--stock", help="指定单个股票代码")
    update_parser.add_argument("--all-pools", action="store_true", help="更新所有股票池中的股票")
    update_parser.add_argument("--type", help="指定更新数据类型，用逗号分隔，如：kline,financial,dividend")
    update_parser.add_argument("--start-date", help="指定历史数据更新的起始日期")
    
    # scan 命令
    scan_parser = subparsers.add_parser("scan", help="执行选股扫描")
    scan_parser.add_argument("--pool", default="default_pool", help="指定要扫描的股票池")
    scan_parser.add_argument("--date", help="指定扫描日期")
    scan_parser.add_argument("--strategy", help="指定运行特定策略")
    
    args = parser.parse_args()
    
    if args.command == "init-config":
        init_config()
    elif args.command == "update-data":
        update_data(args)
    elif args.command == "scan":
        scan(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    # 设置日志
    logger = setup_logger("main", "INFO", "app.log")
    main()
