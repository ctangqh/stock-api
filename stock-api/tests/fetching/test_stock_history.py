import pytest
import pandas as pd
from unittest import mock
from get.stock_history import StockHistoryDataFetcher


@pytest.fixture
def test_db_config():
    """测试数据库配置"""
    return {
        'host': 'localhost',
        'port': 5432,
        'user': 'test',
        'password': 'test',
        'database': 'test'
    }


@pytest.fixture
def test_redis_config():
    """测试 Redis 配置"""
    return {
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }


@pytest.fixture
def test_stock_dataframe():
    """测试用的股票历史数据 DataFrame"""
    data = [
        {
            '日期': '2024-01-01',
            '开盘': 10.0,
            '最高': 11.0,
            '最低': 9.5,
            '收盘': 10.5,
            '成交量': 1000000,
            '成交额': 10500000,
            '换手率': 1.0,
            '振幅': 15.0,
            '涨跌幅': 5.0,
            '涨跌额': 0.5
        },
        {
            '日期': '2024-01-02',
            '开盘': 10.5,
            '最高': 11.5,
            '最低': 10.0,
            '收盘': 11.0,
            '成交量': 1200000,
            '成交额': 13200000,
            '换手率': 1.2,
            '振幅': 14.3,
            '涨跌幅': 4.76,
            '涨跌额': 0.5
        }
    ]
    return pd.DataFrame(data)


@pytest.mark.unit
class TestStockHistoryDataFetcher:
    """测试 StockHistoryDataFetcher 类"""

    def test_fetch_success(self, test_db_config, test_redis_config, test_stock_dataframe):
        """测试从 akshare 成功获取数据"""
        with mock.patch('get.stock_history.ak.stock_zh_a_hist') as mock_ak, \
             mock.patch('get.stock_history.RedisUtil') as mock_redis, \
             mock.patch('get.stock_history.StockCnHistoryMarketORM') as mock_orm:
            
            # 配置 mock
            mock_ak.return_value = test_stock_dataframe
            mock_redis_instance = mock_redis.return_value
            mock_redis_instance.get.return_value = None  # 缓存未命中
            
            # 创建 fetcher 实例
            fetcher = StockHistoryDataFetcher(test_db_config, test_redis_config)
            
            # 调用方法
            result = fetcher.fetch_stock_history('000001', days=30)
            
            # 断言
            assert result is not None
            assert isinstance(result, pd.DataFrame)
            mock_ak.assert_called_once()
            mock_redis_instance.get.assert_called_once()
            mock_redis_instance.set.assert_called_once()

    def test_fetch_cached(self, test_db_config, test_redis_config, test_stock_dataframe):
        """测试从 Redis 缓存获取数据"""
        with mock.patch('get.stock_history.ak.stock_zh_a_hist') as mock_ak, \
             mock.patch('get.stock_history.RedisUtil') as mock_redis, \
             mock.patch('get.stock_history.StockCnHistoryMarketORM') as mock_orm:
            
            # 配置 mock
            cached_data = test_stock_dataframe.to_dict('records')
            mock_redis_instance = mock_redis.return_value
            mock_redis_instance.get.return_value = cached_data  # 缓存命中
            
            # 创建 fetcher 实例
            fetcher = StockHistoryDataFetcher(test_db_config, test_redis_config)
            
            # 调用方法
            result = fetcher.fetch_stock_history('000001', days=30)
            
            # 断言
            assert result is not None
            assert isinstance(result, pd.DataFrame)
            mock_ak.assert_not_called()  # 不应调用 akshare
            mock_redis_instance.get.assert_called_once()
            mock_redis_instance.set.assert_not_called()

    def test_akshare_retry(self, test_db_config, test_redis_config, test_stock_dataframe):
        """测试 akshare 失败后重试逻辑"""
        with mock.patch('get.stock_history.time.sleep') as mock_sleep, \
             mock.patch('get.stock_history.ak.stock_zh_a_hist') as mock_ak, \
             mock.patch('get.stock_history.RedisUtil') as mock_redis, \
             mock.patch('get.stock_history.StockCnHistoryMarketORM') as mock_orm:
            
            # 配置 mock: 前两次抛出异常，第三次成功
            mock_ak.side_effect = [
                Exception("第一次失败"),
                Exception("第二次失败"),
                test_stock_dataframe
            ]
            mock_redis_instance = mock_redis.return_value
            mock_redis_instance.get.return_value = None
            
            # 创建 fetcher 实例
            fetcher = StockHistoryDataFetcher(test_db_config, test_redis_config)
            
            # 调用方法 - 原代码没有重试逻辑，但我们可以测试异常处理
            result = fetcher.fetch_stock_history('000001', days=30)
            
            # 断言 - 原代码只尝试一次，所以第一次异常后就会返回 None
            assert result is None
            assert mock_ak.call_count == 1

    def test_sync_to_database(self, test_db_config, test_redis_config, test_stock_dataframe):
        """测试同步数据到数据库"""
        with mock.patch('get.stock_history.StockCnHistoryMarketORM') as mock_orm, \
             mock.patch('get.stock_history.RedisUtil') as mock_redis:
            
            # 配置 mock
            mock_orm_instance = mock_orm.return_value
            mock_orm_instance.batch_insert.return_value = [1, 2]  # 两条插入成功
            
            # 创建 fetcher 实例
            fetcher = StockHistoryDataFetcher(test_db_config, test_redis_config)
            
            # 调用方法
            success_count = fetcher.sync_to_database(test_stock_dataframe, ts_code='000001')
            
            # 断言
            assert success_count == 2
            mock_orm_instance.batch_insert.assert_called_once()

    def test_sync_empty_dataframe(self, test_db_config, test_redis_config):
        """测试同步空 DataFrame"""
        with mock.patch('get.stock_history.StockCnHistoryMarketORM') as mock_orm, \
             mock.patch('get.stock_history.RedisUtil') as mock_redis:
            
            # 创建空 DataFrame
            empty_df = pd.DataFrame()
            
            # 创建 fetcher 实例
            fetcher = StockHistoryDataFetcher(test_db_config, test_redis_config)
            
            # 调用方法
            success_count = fetcher.sync_to_database(empty_df, ts_code='000001')
            
            # 断言
            assert success_count == 0
            mock_orm.return_value.batch_insert.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
