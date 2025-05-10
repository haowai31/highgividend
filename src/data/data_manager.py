"""
数据管理模块 - 负责股票数据的获取、存储和更新
"""
import logging
import time
from typing import List, Optional, Dict, Any, Union
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta

from .db_handler import DatabaseHandler
from ..utils.logger import setup_logger

class DataManager:
    """数据管理类，负责处理所有数据相关的操作"""
    
    def __init__(self, config_or_db: Union[str, DatabaseHandler]):
        """
        初始化数据管理器
        
        Args:
            config_or_db: 配置文件路径或DatabaseHandler实例
        """
        if isinstance(config_or_db, DatabaseHandler):
            self.db = config_or_db
        else:
            self.db = DatabaseHandler(config_or_db)
        self.logger = setup_logger(__name__)
        
    def initialize_database(self) -> None:
        """初始化数据库表结构"""
        self.db.initialize_tables()
        
    def _fetch_from_akshare(self, func, *args, **kwargs) -> pd.DataFrame:
        """
        从akshare获取数据，包含重试机制
        
        Args:
            func: akshare函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            DataFrame: 获取的数据
        """
        max_retries = self.db.config.get("data_source", {}).get("akshare_max_retries", 3)
        retry_delay = self.db.config.get("data_source", {}).get("akshare_retry_delay_seconds", 10)
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"从akshare获取数据失败: {str(e)}")
                    raise
                self.logger.warning(f"第{attempt + 1}次尝试失败，{retry_delay}秒后重试")
                time.sleep(retry_delay)
                
    def get_stock_daily_kline(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票日K线数据（使用 akshare_rules.md 推荐接口）
        """
        query = """
            SELECT * FROM daily_kline 
            WHERE stock_code = ? AND date BETWEEN ? AND ?
            ORDER BY date
        """
        df = self.db.execute_query(query, (stock_code, start_date, end_date))
        if df is not None and not df.empty:
            self.logger.info(f"从数据库获取到{stock_code}的日K线数据")
            return df
        self.logger.info(f"从akshare获取{stock_code}的日K线数据")
        try:
            # 去掉市场前缀
            symbol = stock_code[2:]
            # 确保日期格式正确
            start_date = pd.to_datetime(start_date).strftime('%Y%m%d')
            end_date = pd.to_datetime(end_date).strftime('%Y%m%d')
            
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            self.logger.info(f"akshare返回日K线数据行数: {len(df)}")
            if df.empty:
                self.logger.warning(f"akshare返回的日K线数据为空")
                return pd.DataFrame()
                
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount',
            })
            
            # 确保日期格式统一
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df['stock_code'] = stock_code
            df['adj_factor'] = 1.0
            
            # 只保留需要的字段
            keep_cols = ['stock_code', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'adj_factor']
            df = df[[col for col in keep_cols if col in df.columns]]
            
            # 过滤主键为空的行
            df = df[df['date'].notna()]
            if df.empty:
                self.logger.warning(f"过滤后的日K线数据为空，未插入数据库")
                return pd.DataFrame()
                
            self.db.insert_dataframe('daily_kline', df)
            return df
        except Exception as e:
            self.logger.error(f"从akshare获取{stock_code}的日K线数据失败: {str(e)}")
            return pd.DataFrame()
        
    def get_stock_financial_summary(self, stock_code: str) -> pd.DataFrame:
        """
        获取股票财务摘要数据（使用 akshare_rules.md 推荐接口）
        """
        query = """
            SELECT * FROM financial_summary 
            WHERE stock_code = ?
            ORDER BY date DESC
            LIMIT 1
        """
        df = self.db.execute_query(query, (stock_code,))
        if df is not None and not df.empty:
            self.logger.info(f"从数据库获取到{stock_code}的财务摘要数据")
            return df
        self.logger.info(f"从akshare获取{stock_code}的财务摘要数据")
        try:
            # 去掉市场前缀
            symbol = stock_code[2:]
            df = ak.stock_a_indicator_lg(symbol=symbol)
            self.logger.info(f"akshare返回财务摘要数据行数: {len(df)}")
            self.logger.info(f"akshare返回财务摘要数据列名: {df.columns.tolist()}")
            
            if df.empty:
                self.logger.warning(f"akshare返回的财务摘要数据为空")
                return pd.DataFrame()
            
            # 检查并打印数据结构
            self.logger.info(f"数据预览:\n{df.head()}")
            
            # 重命名列（根据实际返回的列名调整）
            column_mapping = {
                'trade_date': 'date',  # 如果日期列名是 trade_date
                'pe_ttm': 'pe_ttm',    # 如果市盈率列名是 pe_ttm
                'pb': 'pb_mrq',        # 如果市净率列名是 pb
                'total_mv': 'market_cap',  # 如果总市值列名是 total_mv
                'circ_mv': 'circulating_market_cap'  # 如果流通市值列名是 circ_mv
            }
            
            # 只重命名存在的列
            rename_dict = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=rename_dict)
            
            # 确保日期格式统一
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            else:
                self.logger.error(f"未找到日期列，当前列名: {df.columns.tolist()}")
                return pd.DataFrame()
            
            df['stock_code'] = stock_code
            
            # 只保留需要的字段
            keep_cols = ['stock_code', 'date', 'pe_ttm', 'pb_mrq', 'market_cap', 'circulating_market_cap']
            available_cols = [col for col in keep_cols if col in df.columns]
            if len(available_cols) < 2:  # 至少需要 stock_code 和 date
                self.logger.error(f"可用列数不足，当前可用列: {available_cols}")
                return pd.DataFrame()
            
            df = df[available_cols]
            
            # 过滤主键为空的行
            df = df[df['date'].notna()]
            if df.empty:
                self.logger.warning(f"过滤后的财务摘要数据为空，未插入数据库")
                return pd.DataFrame()
            
            self.db.insert_dataframe('financial_summary', df)
            return df
        except Exception as e:
            self.logger.error(f"从akshare获取{stock_code}的财务摘要数据失败: {str(e)}")
            self.logger.error(f"错误详情: {type(e).__name__}")
            return pd.DataFrame()
        
    def get_stock_dividend_data(self, stock_code: str) -> pd.DataFrame:
        """
        获取股票分红数据（使用 akshare_rules.md 推荐接口）
        """
        query = """
            SELECT * FROM dividend_data 
            WHERE stock_code = ?
            ORDER BY ex_dividend_date DESC
        """
        df = self.db.execute_query(query, (stock_code,))
        if df is not None and not df.empty:
            self.logger.info(f"从数据库获取到{stock_code}的分红数据")
            return df
        self.logger.info(f"从akshare获取{stock_code}的分红数据")
        try:
            symbol = stock_code[2:]
            df = ak.stock_history_dividend_detail(symbol=symbol)
            self.logger.info(f"akshare返回分红数据行数: {len(df)}")
            df = df.rename(columns={
                '公告日期': 'report_date',
                '除权除息日': 'ex_dividend_date',
                '每股股利(税前)': 'dividend_per_share_pre_tax',
            })
            df['stock_code'] = stock_code
            keep_cols = ['stock_code', 'report_date', 'ex_dividend_date', 'dividend_per_share_pre_tax']
            if 'dividend_per_share_pre_tax' in df.columns:
                df['dividend_yield'] = df['dividend_per_share_pre_tax'] / 100
                keep_cols.append('dividend_yield')
            df = df[[col for col in keep_cols if col in df.columns]]
            # 过滤主键为空的行
            df = df[df['ex_dividend_date'].notna()]
            if df.empty:
                self.logger.warning(f"akshare返回的分红数据全部为空，未插入数据库")
                return pd.DataFrame()
            self.db.insert_dataframe('dividend_data', df)
            return df
        except Exception as e:
            self.logger.error(f"从akshare获取{stock_code}的分红数据失败: {str(e)}")
            return pd.DataFrame()
        
    def update_single_stock_data(self, 
                                stock_code: str, 
                                data_types: List[str] = ['kline', 'financial', 'dividend']) -> None:
        """
        更新单只股票的指定类型数据
        
        Args:
            stock_code: 股票代码
            data_types: 要更新的数据类型列表
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        for data_type in data_types:
            try:
                if data_type == 'kline':
                    self.get_stock_daily_kline(stock_code, start_date, end_date)
                elif data_type == 'financial':
                    self.get_stock_financial_summary(stock_code)
                elif data_type == 'dividend':
                    self.get_stock_dividend_data(stock_code)
                else:
                    self.logger.warning(f"未知的数据类型: {data_type}")
            except Exception as e:
                self.logger.error(f"更新{stock_code}的{data_type}数据失败: {str(e)}")
                
    def batch_update_stock_data(self, 
                               stock_codes: List[str], 
                               data_types: List[str] = ['kline', 'financial', 'dividend']) -> None:
        """
        批量更新多只股票的数据
        
        Args:
            stock_codes: 股票代码列表
            data_types: 要更新的数据类型列表
        """
        for stock_code in stock_codes:
            self.update_single_stock_data(stock_code, data_types)
            
    def calculate_and_store_derived_kline(self, 
                                         stock_code: str, 
                                         period: str = 'weekly') -> None:
        """
        计算并存储派生的K线数据（周线/月线）
        
        Args:
            stock_code: 股票代码
            period: 周期类型 ('weekly' 或 'monthly')
        """
        # 获取日K线数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        daily_df = self.get_stock_daily_kline(stock_code, start_date, end_date)
        
        if daily_df is None or daily_df.empty:
            self.logger.warning(f"无法计算{stock_code}的{period}K线：没有日K线数据")
            return
            
        # 转换日期列为datetime类型
        daily_df['date'] = pd.to_datetime(daily_df['date'])
        
        # 设置日期为索引
        daily_df.set_index('date', inplace=True)
        
        # 根据周期重采样
        if period == 'weekly':
            resampled = daily_df.resample('W').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'amount': 'sum',
                'adj_factor': 'last'
            })
            target_table = 'weekly_kline'
        else:  # monthly
            resampled = daily_df.resample('M').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'amount': 'sum',
                'adj_factor': 'last'
            })
            target_table = 'monthly_kline'
            
        # 重置索引，将日期变回列
        resampled.reset_index(inplace=True)
        
        # 添加股票代码列
        resampled['stock_code'] = stock_code
        
        # 将日期格式化为字符串
        resampled['date'] = resampled['date'].dt.strftime('%Y-%m-%d')
        
        # 存储到数据库
        self.db.insert_dataframe(target_table, resampled)
        
        # 记录更新日志
        self.record_data_update_log(target_table, stock_code, end_date)
        
    def calculate_dynamic_dividend_yield(self, 
                                        stock_code: str, 
                                        current_price: float, 
                                        date_for_dividend_history: str) -> float:
        """
        计算动态股息率
        
        Args:
            stock_code: 股票代码
            current_price: 当前价格
            date_for_dividend_history: 用于计算股息率的历史日期
            
        Returns:
            float: 动态股息率
        """
        # 获取分红数据
        dividend_df = self.get_stock_dividend_data(stock_code)
        
        if dividend_df is None or dividend_df.empty:
            self.logger.warning(f"无法计算{stock_code}的动态股息率：没有分红数据")
            return 0.0
            
        # 过滤出指定日期之前的分红数据
        dividend_df['ex_dividend_date'] = pd.to_datetime(dividend_df['ex_dividend_date'])
        date_for_dividend_history = pd.to_datetime(date_for_dividend_history)
        recent_dividends = dividend_df[dividend_df['ex_dividend_date'] <= date_for_dividend_history]
        
        if recent_dividends.empty:
            return 0.0
            
        # 计算近12个月的分红总额
        one_year_ago = date_for_dividend_history - pd.DateOffset(years=1)
        yearly_dividends = recent_dividends[recent_dividends['ex_dividend_date'] > one_year_ago]
        
        if yearly_dividends.empty:
            return 0.0
            
        total_dividend = yearly_dividends['dividend_per_share_pre_tax'].sum()
        
        # 计算动态股息率
        dividend_yield = (total_dividend / current_price) * 100
        
        return dividend_yield
        
    def record_data_update_log(self, 
                              table_name: str, 
                              stock_code: str, 
                              last_fetch_date: str) -> None:
        """
        记录数据更新日志
        
        Args:
            table_name: 表名
            stock_code: 股票代码
            last_fetch_date: 最后获取数据的日期
        """
        query = """
            INSERT OR REPLACE INTO data_update_log 
            (table_name, stock_code, last_update_date, last_successful_fetch_date_for_stock)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_update(query, (table_name, stock_code, last_fetch_date, last_fetch_date)) 