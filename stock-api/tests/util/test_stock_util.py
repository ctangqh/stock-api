import pytest
from unittest import mock
from datetime import date, timedelta
from util.StockUtil import (
    get_stock_technical_indicators,
    batch_get_stock_indicators,
    get_latest_stock_indicators
)


@pytest.fixture
def test_stock_history_data():
    """测试用的股票历史数据"""
    today = date.today()
    data = []
    for i in range(60):
        data_date = today - timedelta(days=59 - i)
        data.append({
            'stock_code': '000001',
            'data_date': data_date,
            'open': 10.0 + i * 0.1,
            'high': 10.5 + i * 0.1,
            'low': 9.5 + i * 0.1,
            'close': 10.0 + i * 0.1,
            'volume': 1000000,
            'amount': 10000000
        })
    return data


@pytest.mark.unit
class TestStockUtil:
    """测试 StockUtil 模块"""

    def test_get_stock_technical_indicators_success(self, test_stock_history_data):
        """测试成功获取股票技术指标"""
        with mock.patch('util.StockUtil.StockCnHistoryMarketORM') as mock_orm:
            # 配置 mock
            mock_orm_instance = mock_orm.return_value
            mock_orm_instance.get_by_code_and_date_range.return_value = test_stock_history_data
            
            # 调用方法
            today = date.today()
            result = get_stock_technical_indicators('000001', today, days_back=60)
            
            # 断言
            assert isinstance(result, list)
            assert len(result) == 60
            for record in result:
                assert 'ma5' in record
                assert 'ma10' in record
                assert 'ma20' in record
                assert 'ma60' in record
                assert 'macd_dif' in record
                assert 'macd_dea' in record
                assert 'macd_hist' in record

    def test_get_stock_technical_indicators_no_data(self):
        """测试没有历史数据的情况"""
        with mock.patch('util.StockUtil.StockCnHistoryMarketORM') as mock_orm:
            mock_orm_instance = mock_orm.return_value
            mock_orm_instance.get_by_code_and_date_range.return_value = []
            
            today = date.today()
            result = get_stock_technical_indicators('000001', today)
            
            assert result == []

    def test_batch_get_stock_indicators_success(self, test_stock_history_data):
        """测试批量获取股票技术指标"""
        with mock.patch('util.StockUtil.StockCnHistoryMarketORM') as mock_orm:
            mock_orm_instance = mock_orm.return_value
            mock_orm_instance.get_by_code_and_date_range.return_value = test_stock_history_data
            
            stock_codes = ['000001', '000002', '000003']
            today = date.today()
            result = batch_get_stock_indicators(stock_codes, today)
            
            assert isinstance(result, dict)
            assert len(result) == 3
            for code in stock_codes:
                assert code in result
                assert isinstance(result[code], list)

    def test_batch_get_stock_indicators_with_exception(self, test_stock_history_data):
        """测试批量获取时部分股票失败的情况"""
        with mock.patch('util.StockUtil.StockCnHistoryMarketORM') as mock_orm:
            mock_orm_instance = mock_orm.return_value
            
            # 第一个股票成功，第二个失败
            def side_effect(code, *args, **kwargs):
                if code == '000001':
                    return test_stock_history_data
                raise Exception("测试异常")
            
            mock_orm_instance.get_by_code_and_date_range.side_effect = side_effect
            
            stock_codes = ['000001', '000002']
            today = date.today()
            result = batch_get_stock_indicators(stock_codes, today)
            
            assert isinstance(result, dict)
            assert len(result) == 2
            assert len(result['000001']) > 0
            assert result['000002'] == []

    def test_get_latest_stock_indicators(self, test_stock_history_data):
        """测试获取最新技术指标"""
        with mock.patch('util.StockUtil.StockCnHistoryMarketORM') as mock_orm:
            mock_orm_instance = mock_orm.return_value
            mock_orm_instance.get_by_code_and_date_range.return_value = test_stock_history_data
            
            result = get_latest_stock_indicators('000001', days=60)
            
            assert isinstance(result, list)
            assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__])
