import pytest
from unittest import mock
from datetime import date
from job.stock_scan import screen_stocks


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


@pytest.mark.unit
class TestStockScan:
    """测试股票筛选功能"""

    def test_screen_stocks_success(self, test_db_config):
        """测试成功筛选股票"""
        with mock.patch('job.stock_scan.StockChooseStrategyORM') as mock_strategy_orm, \
             mock.patch('job.stock_scan.StockBestChooseORM') as mock_best_choose_orm, \
             mock.patch('job.stock_scan.StockCnHistoryMarketORM') as mock_market_orm, \
             mock.patch('util.StockUtil.batch_get_stock_indicators') as mock_batch_get_indicators, \
             mock.patch('strategy.choose_service.detect_death_cross') as mock_detect_death_cross, \
             mock.patch('job.stock_scan.DB_CONFIG', test_db_config):
            
            # 配置 mock
            mock_strategy_instance = mock_strategy_orm.return_value
            mock_best_choose_instance = mock_best_choose_orm.return_value
            mock_market_instance = mock_market_orm.return_value
            
            # 模拟策略数据
            mock_strategy_instance.get_all_active.return_value = [
                {
                    'name': 'test_strategy',
                    'value': {
                        'min_change_percent': 3.0,
                        'max_change_percent': 6.0,
                        'check_ma20': True,
                        'check_macd': True,
                        'check_recent_rise': True,
                        'recent_days': 3
                    }
                }
            ]
            
            # 模拟市场数据
            mock_market_instance.get_by_data_date.return_value = [
                {
                    'code': '000001',
                    'name': '平安银行',
                    'close': 10.5,
                    'change_percent': 4.5,
                    'ma20': 10.0,
                    'macd_dif': 0.1,
                    'macd_dea': 0.05
                }
            ]
            
            # 模拟 batch_get_stock_indicators 返回值
            mock_batch_get_indicators.return_value = {
                '000001': [
                    {'data_date': date(2024, 1, 1), 'ma20': 10.0, 'macd_dif': 0.1, 'macd_dea': 0.05},
                    {'data_date': date(2024, 1, 2), 'ma20': 10.0, 'macd_dif': 0.1, 'macd_dea': 0.05},
                    {'data_date': date(2024, 1, 3), 'ma20': 10.0, 'macd_dif': 0.1, 'macd_dea': 0.05},
                ] * 20  # 足够的数据量
            }
            
            # 模拟 detect_death_cross 返回值 (没有死叉)
            mock_detect_death_cross.return_value = []
            
            # 模拟获取股票历史数据 (最近3天都是上涨的)
            mock_market_instance.get_by_code.return_value = [
                {'data_date': date(2024, 1, 1), 'change_percent': 1.0},
                {'data_date': date(2024, 1, 2), 'change_percent': 2.0},
                {'data_date': date(2024, 1, 3), 'change_percent': 3.0},
                {'data_date': date(2023, 12, 31), 'change_percent': 0.5},
            ]
            
            # 调用函数
            screen_stocks(date(2024, 1, 3))
            
            # 断言
            mock_strategy_instance.get_all_active.assert_called_once()
            mock_market_instance.get_by_data_date.assert_called_once()
            mock_best_choose_instance.batch_insert.assert_called_once()
            mock_strategy_instance.close.assert_called_once()
            mock_best_choose_instance.close.assert_called_once()
            mock_market_instance.close.assert_called_once()

    def test_screen_stocks_no_strategies(self, test_db_config):
        """测试没有激活策略的情况"""
        with mock.patch('job.stock_scan.StockChooseStrategyORM') as mock_strategy_orm, \
             mock.patch('job.stock_scan.StockBestChooseORM') as mock_best_choose_orm, \
             mock.patch('job.stock_scan.StockCnHistoryMarketORM') as mock_market_orm, \
             mock.patch('job.stock_scan.DB_CONFIG', test_db_config):
            
            # 配置 mock: 没有激活的策略
            mock_strategy_instance = mock_strategy_orm.return_value
            mock_strategy_instance.get_all_active.return_value = []
            
            # 调用函数
            screen_stocks(date(2024, 1, 3))
            
            # 断言
            mock_strategy_instance.get_all_active.assert_called_once()
            mock_best_choose_orm.return_value.batch_insert.assert_not_called()

    def test_screen_stocks_error_handling(self, test_db_config):
        """测试异常处理"""
        with mock.patch('job.stock_scan.StockChooseStrategyORM') as mock_strategy_orm, \
             mock.patch('job.stock_scan.StockBestChooseORM') as mock_best_choose_orm, \
             mock.patch('job.stock_scan.StockCnHistoryMarketORM') as mock_market_orm, \
             mock.patch('job.stock_scan.DB_CONFIG', test_db_config):
            
            # 配置 mock: 抛出异常
            mock_strategy_instance = mock_strategy_orm.return_value
            mock_strategy_instance.get_all_active.side_effect = Exception("数据库连接失败")
            
            # 调用函数 (不应抛出异常)
            screen_stocks(date(2024, 1, 3))
            
            # 断言
            mock_strategy_instance.get_all_active.assert_called_once()
            mock_strategy_instance.close.assert_called_once()
            mock_best_choose_orm.return_value.close.assert_called_once()
            mock_market_orm.return_value.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
