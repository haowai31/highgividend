"""
数据库处理模块 - 负责数据库的初始化、连接和基本操作
"""
import json
import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

class DatabaseHandler:
    """数据库处理类，负责处理所有数据库相关的操作"""
    
    def __init__(self, config: Union[str, Dict[str, Any]]):
        """
        初始化数据库处理器
        
        Args:
            config: 配置文件路径或配置字典
        """
        self.config = self._load_config(config)
        self.conn = None
        self.connect()
        
    def _load_config(self, config: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        加载配置
        
        Args:
            config: 配置文件路径或配置字典
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        if isinstance(config, dict):
            return config
            
        try:
            with open(config, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，返回默认配置
            return {
                "database_path": "stock_data.db",
                "log_level": "INFO",
                "log_file_path": "app.log"
            }
            
    def connect(self) -> None:
        """连接到数据库"""
        try:
            self.conn = sqlite3.connect(self.config["database_path"])
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")
            
    def close(self) -> None:
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            
    def initialize_tables(self) -> None:
        """初始化数据库表结构"""
        self.connect()
        cursor = self.conn.cursor()
        # 日K线表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_kline (
                stock_code TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                amount REAL,
                adj_factor REAL,
                PRIMARY KEY (stock_code, date)
            )
        ''')
        # 周K线表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_kline (
                stock_code TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                amount REAL,
                adj_factor REAL,
                PRIMARY KEY (stock_code, date)
            )
        ''')
        # 月K线表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_kline (
                stock_code TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                amount REAL,
                adj_factor REAL,
                PRIMARY KEY (stock_code, date)
            )
        ''')
        
        # 创建分红数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dividend_data (
                stock_code TEXT NOT NULL,
                report_date TEXT,
                ex_dividend_date TEXT NOT NULL,
                dividend_per_share_pre_tax REAL,
                dividend_yield REAL,
                PRIMARY KEY (stock_code, ex_dividend_date)
            )
        """)
        
        # 创建财务摘要表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_summary (
                stock_code TEXT NOT NULL,
                date TEXT NOT NULL,
                pe_ttm REAL,
                pb_mrq REAL,
                market_cap REAL,
                circulating_market_cap REAL,
                PRIMARY KEY (stock_code, date)
            )
        """)
        
        # 创建历史信号表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                date TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                price REAL,
                description TEXT
            )
        """)
        
        # 创建数据更新日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_update_log (
                table_name TEXT NOT NULL,
                stock_code TEXT NOT NULL,
                last_update_date TEXT NOT NULL,
                last_successful_fetch_date_for_stock TEXT,
                PRIMARY KEY (table_name, stock_code)
            )
        """)
        
        self.conn.commit()
            
    def execute_query(self, query: str, params: tuple = None) -> Optional[pd.DataFrame]:
        """
        执行查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            Optional[pd.DataFrame]: 查询结果
        """
        try:
            if params:
                return pd.read_sql_query(query, self.conn, params=params)
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            raise Exception(f"执行查询失败: {str(e)}")
            
    def execute_update(self, query: str, params: tuple = None) -> None:
        """
        执行更新操作
        
        Args:
            query: SQL更新语句
            params: 更新参数
        """
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"执行更新失败: {str(e)}")
            
    def insert_dataframe(self, table_name: str, df: pd.DataFrame) -> None:
        """
        将DataFrame数据插入到指定表
        
        Args:
            table_name: 表名
            df: 要插入的数据
        """
        try:
            df.to_sql(table_name, self.conn, if_exists='append', index=False)
        except Exception as e:
            raise Exception(f"插入数据失败: {str(e)}") 