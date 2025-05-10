"""
pytest配置文件，包含测试用的fixture
"""
import os
import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.data.data_manager import DataManager
from src.data.db_handler import DatabaseHandler

@pytest.fixture
def test_config():
    """测试用的配置"""
    return {
        "data_source": {
            "akshare_max_retries": 2,
            "akshare_retry_delay_seconds": 1
        },
        "database_path": "test_stock_data.db",
        "log_level": "DEBUG",
        "log_file_path": "test_app.log"
    }

@pytest.fixture
def test_db(test_config):
    """测试用的数据库处理器"""
    db = DatabaseHandler(test_config)
    db.initialize_tables()
    yield db
    # 清理测试数据库
    if os.path.exists(test_config["database_path"]):
        os.remove(test_config["database_path"])

@pytest.fixture
def test_data_manager(test_config):
    """测试用的数据管理器"""
    manager = DataManager(test_config)
    manager.initialize_database()
    return manager

@pytest.fixture
def sample_daily_kline_data():
    """测试用的日K线数据"""
    dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D')
    data = {
        'date': dates,
        'open': [100.0] * len(dates),
        'high': [105.0] * len(dates),
        'low': [95.0] * len(dates),
        'close': [102.0] * len(dates),
        'volume': [1000000] * len(dates),
        'amount': [100000000] * len(dates),
        'adj_factor': [1.0] * len(dates),
        'stock_code': ['SH600000'] * len(dates)
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_financial_data():
    """测试用的财务数据"""
    data = {
        'date': ['2024-01-01'],
        'pe_ttm': [15.0],
        'pb_mrq': [1.5],
        'market_cap': [1000000000],
        'circulating_market_cap': [800000000],
        'stock_code': ['SH600000']
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_dividend_data():
    """测试用的分红数据"""
    data = {
        'report_date': ['2023-12-01', '2022-12-01'],
        'ex_dividend_date': ['2023-12-15', '2022-12-15'],
        'dividend_per_share_pre_tax': [1.0, 0.8],
        'stock_code': ['SH600000', 'SH600000']
    }
    return pd.DataFrame(data) 