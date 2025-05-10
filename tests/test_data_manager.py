"""
测试数据管理模块的功能
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.data.data_manager import DataManager
from src.data.db_handler import DatabaseHandler
import akshare as ak

@pytest.fixture
def db_handler():
    """创建测试用的数据库处理器"""
    db = DatabaseHandler({
        "database_path": ":memory:",
        "data_source": {
            "akshare_max_retries": 3,
            "akshare_retry_delay_seconds": 1
        }
    })
    db.initialize_tables()  # 确保表被创建
    return db

@pytest.fixture
def data_manager(db_handler):
    """创建测试用的数据管理器"""
    return DataManager(db_handler)

def test_initialize_database(data_manager):
    """测试数据库初始化"""
    data_manager.initialize_database()
    tables = data_manager.db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
    # 排除sqlite_sequence表
    tables = tables[~tables['name'].isin(['sqlite_sequence'])]
    assert len(tables) == 7
    assert 'daily_kline' in tables['name'].values
    assert 'weekly_kline' in tables['name'].values
    assert 'monthly_kline' in tables['name'].values
    assert 'dividend_data' in tables['name'].values
    assert 'financial_summary' in tables['name'].values
    assert 'historical_signals' in tables['name'].values
    assert 'data_update_log' in tables['name'].values

def test_get_stock_daily_kline_from_db(data_manager):
    """测试从数据库获取日K线数据"""
    # 插入测试数据
    test_data = pd.DataFrame({
        'stock_code': ['SH600036'] * 2,
        'date': ['2023-01-01', '2023-01-02'],
        'open': [10.0, 10.1],
        'high': [10.5, 10.6],
        'low': [9.8, 9.9],
        'close': [10.2, 10.3],
        'volume': [1000, 1100],
        'amount': [10000, 11000],
        'adj_factor': [1.0, 1.0]
    })
    data_manager.db.insert_dataframe('daily_kline', test_data)
    
    # 测试获取数据
    df = data_manager.get_stock_daily_kline('SH600036', '2023-01-01', '2023-01-02')
    assert not df.empty
    assert len(df) == 2
    assert 'open' in df.columns
    assert 'close' in df.columns

def test_get_stock_daily_kline_from_akshare(data_manager, mocker):
    """测试从akshare获取日K线数据"""
    # 模拟akshare返回的数据
    mock_data = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-02'],
        'open': [10.0, 10.1],
        'high': [10.5, 10.6],
        'low': [9.8, 9.9],
        'close': [10.2, 10.3],
        'volume': [1000, 1100],
        'amount': [10000, 11000]
    })
    mocker.patch('akshare.stock_zh_a_hist', return_value=mock_data)
    
    df = data_manager.get_stock_daily_kline('SH600036', '2023-01-01', '2023-01-02')
    assert not df.empty
    assert len(df) == 2
    assert 'open' in df.columns
    assert 'close' in df.columns

def test_get_stock_financial_summary_from_db(data_manager):
    """测试从数据库获取财务摘要数据"""
    # 插入测试数据
    test_data = pd.DataFrame({
        'stock_code': ['SH600036'],
        'date': ['2023-01-01'],
        'pe_ttm': [10.0],
        'pb_mrq': [1.5],
        'market_cap': [1000000],
        'circulating_market_cap': [800000]
    })
    data_manager.db.insert_dataframe('financial_summary', test_data)
    
    # 测试获取数据
    df = data_manager.get_stock_financial_summary('SH600036')
    assert not df.empty
    assert 'pe_ttm' in df.columns
    assert 'pb_mrq' in df.columns

def test_get_stock_financial_summary_from_akshare(data_manager, mocker):
    """测试从akshare获取财务摘要数据"""
    # 模拟akshare返回的数据
    mock_data = pd.DataFrame({
        'date': ['2023-01-01'],
        'pe_ttm': [10.0],
        'pb_mrq': [1.5],
        'market_cap': [1000000],
        'circulating_market_cap': [800000]
    })
    
    # 如果akshare模块没有stock_a_lg_indicator属性，先添加它
    if not hasattr(ak, 'stock_a_lg_indicator'):
        ak.stock_a_lg_indicator = lambda symbol: mock_data
    
    # 使用patch.object进行mock
    mocker.patch.object(ak, 'stock_a_lg_indicator', return_value=mock_data)
    
    df = data_manager.get_stock_financial_summary('SH600036')
    assert not df.empty
    assert 'pe_ttm' in df.columns
    assert 'pb_mrq' in df.columns

def test_get_stock_dividend_data_from_db(data_manager):
    """测试从数据库获取分红数据"""
    # 插入测试数据
    test_data = pd.DataFrame({
        'stock_code': ['SH600036'],
        'report_date': ['2023-01-01'],
        'ex_dividend_date': ['2023-01-15'],
        'dividend_per_share_pre_tax': [0.5],
        'dividend_yield': [3.0]
    })
    data_manager.db.insert_dataframe('dividend_data', test_data)
    
    # 测试获取数据
    df = data_manager.get_stock_dividend_data('SH600036')
    assert not df.empty
    assert 'dividend_per_share_pre_tax' in df.columns
    assert 'dividend_yield' in df.columns

def test_get_stock_dividend_data_from_akshare(data_manager, mocker):
    """测试从akshare获取分红数据"""
    # 模拟akshare返回的数据
    mock_data = pd.DataFrame({
        'report_date': ['2023-01-01'],
        'ex_dividend_date': ['2023-01-15'],
        'dividend_per_share_pre_tax': [0.5],
        'dividend_yield': [3.0]
    })
    mocker.patch('akshare.stock_history_dividend_detail', return_value=mock_data)
    
    df = data_manager.get_stock_dividend_data('SH600036')
    assert not df.empty
    assert 'dividend_per_share_pre_tax' in df.columns
    assert 'dividend_yield' in df.columns

def test_calculate_and_store_derived_kline(data_manager):
    """测试计算和存储衍生K线数据"""
    # 插入日K线测试数据，日期覆盖当前时间范围
    from datetime import datetime, timedelta
    base_date = datetime.now() - timedelta(days=4)
    test_data = pd.DataFrame({
        'stock_code': ['SH600036'] * 5,
        'date': [(base_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)],
        'open': [10.0, 10.1, 10.2, 10.3, 10.4],
        'high': [10.5, 10.6, 10.7, 10.8, 10.9],
        'low': [9.8, 9.9, 10.0, 10.1, 10.2],
        'close': [10.2, 10.3, 10.4, 10.5, 10.6],
        'volume': [1000, 1100, 1200, 1300, 1400],
        'amount': [10000, 11000, 12000, 13000, 14000],
        'adj_factor': [1.0] * 5
    })
    data_manager.db.insert_dataframe('daily_kline', test_data)
    
    # 测试计算周K线
    data_manager.calculate_and_store_derived_kline('SH600036', 'weekly')
    weekly_data = data_manager.db.execute_query(
        "SELECT * FROM weekly_kline WHERE stock_code = 'SH600036'"
    )
    assert not weekly_data.empty
    assert len(weekly_data) == 1  # 一周的数据

def test_calculate_dynamic_dividend_yield(data_manager):
    """测试计算动态股息率"""
    # 插入分红测试数据
    test_data = pd.DataFrame({
        'stock_code': ['SH600036'],
        'report_date': ['2023-01-01'],
        'ex_dividend_date': ['2023-01-15'],
        'dividend_per_share_pre_tax': [0.5],
        'dividend_yield': [3.0]
    })
    data_manager.db.insert_dataframe('dividend_data', test_data)
    
    # 测试计算动态股息率
    yield_rate = data_manager.calculate_dynamic_dividend_yield(
        'SH600036',
        16.67,  # 当前价格
        '2023-01-15'  # 计算日期
    )
    assert yield_rate > 0
    assert abs(yield_rate - 3.0) < 0.1  # 允许0.1%的误差

def test_record_data_update_log(data_manager):
    """测试记录数据更新日志"""
    data_manager.record_data_update_log(
        'daily_kline',
        'SH600036',
        '2023-01-01'
    )
    
    log_data = data_manager.db.execute_query(
        "SELECT * FROM data_update_log WHERE table_name = 'daily_kline' AND stock_code = 'SH600036'"
    )
    assert not log_data.empty
    assert log_data.iloc[0]['last_update_date'] == '2023-01-01'
    assert log_data.iloc[0]['last_successful_fetch_date_for_stock'] == '2023-01-01'

def test_update_single_stock_data(data_manager, mocker):
    """测试更新单只股票数据"""
    # 模拟数据获取函数
    mock_get_kline = mocker.patch.object(data_manager, 'get_stock_daily_kline')
    mock_get_financial = mocker.patch.object(data_manager, 'get_stock_financial_summary')
    mock_get_dividend = mocker.patch.object(data_manager, 'get_stock_dividend_data')
    
    # 测试更新所有数据类型
    data_manager.update_single_stock_data('SH600036')
    mock_get_kline.assert_called_once()
    mock_get_financial.assert_called_once()
    mock_get_dividend.assert_called_once()
    
    # 测试只更新部分数据类型
    mock_get_kline.reset_mock()
    mock_get_financial.reset_mock()
    mock_get_dividend.reset_mock()
    
    data_manager.update_single_stock_data('SH600036', ['kline', 'financial'])
    mock_get_kline.assert_called_once()
    mock_get_financial.assert_called_once()
    mock_get_dividend.assert_not_called()

def test_batch_update_stock_data(data_manager, mocker):
    """测试批量更新股票数据"""
    # 模拟更新单只股票的函数
    mock_update_single = mocker.patch.object(data_manager, 'update_single_stock_data')
    
    # 测试批量更新
    stock_codes = ['SH600036', 'SZ000001']
    data_manager.batch_update_stock_data(stock_codes)
    
    assert mock_update_single.call_count == 2
    mock_update_single.assert_any_call('SH600036', ['kline', 'financial', 'dividend'])
    mock_update_single.assert_any_call('SZ000001', ['kline', 'financial', 'dividend']) 