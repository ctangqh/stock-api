from datetime import date
import logging
from job.scan.run import run_scan_job, get_scan_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_mock_stocks():
    """创建模拟股票数据"""
    return [
        {
            'code': '000001',
            'name': '平安银行',
            'close': 12.5,
            'change_percent': 4.5,
            'ma5': 12.0,
            'ma10': 11.8,
            'ma20': 11.5,
            'ma60': 10.8
        },
        {
            'code': '000002',
            'name': '万科A',
            'close': 8.2,
            'change_percent': 2.0,
            'ma5': 8.0,
            'ma10': 7.9,
            'ma20': 7.8,
            'ma60': 7.5
        },
        {
            'code': '600000',
            'name': '浦发银行',
            'close': 9.8,
            'change_percent': 5.2,
            'ma5': 9.5,
            'ma10': 9.3,
            'ma20': 9.0,
            'ma60': 8.7
        }
    ]


def create_mock_market_caps():
    """创建模拟市值数据"""
    return {
        '000001': 250.0,
        '000002': 320.0,
        '600000': 280.0
    }


def create_mock_indicators():
    """创建模拟指标数据"""
    return {
        '000001': {'ma5': 12.0, 'ma10': 11.8, 'ma20': 11.5, 'ma60': 10.8},
        '000002': {'ma5': 8.0, 'ma10': 7.9, 'ma20': 7.8, 'ma60': 7.5},
        '600000': {'ma5': 9.5, 'ma10': 9.3, 'ma20': 9.0, 'ma60': 8.7}
    }


def test_complete_json_strategy():
    """测试完整的 JSON 策略配置"""
    logger.info("\n" + "="*60)
    logger.info("测试 1: 完整的 JSON 策略配置")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    market_caps = create_mock_market_caps()
    indicators = create_mock_indicators()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "filters": [
            {
                "type": "change_percent",
                "params": {
                    "min_change": 3.0,
                    "max_change": 6.0
                }
            },
            {
                "type": "market_cap",
                "params": {
                    "min_cap": 200.0,
                    "max_cap": 350.0
                }
            },
            {
                "type": "ma",
                "params": {
                    "ma_period": 20,
                    "operator": ">="
                }
            }
        ]
    }
    
    logger.info(f"策略配置: {strategy_config}")
    
    result = run_scan_job(
        strategy_config,
        stocks,
        scan_date,
        stock_market_caps=market_caps,
        stock_latest_indicator=indicators
    )
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']}")


def test_single_filter():
    """测试单个过滤器"""
    logger.info("\n" + "="*60)
    logger.info("测试 2: 单个过滤器")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "filters": [
            {
                "type": "change_percent",
                "params": {
                    "min_change": 4.0,
                    "max_change": 5.5
                }
            }
        ]
    }
    
    logger.info(f"策略配置: {strategy_config}")
    
    result = run_scan_job(strategy_config, stocks, scan_date)
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']}")


def test_empty_strategy():
    """测试空策略"""
    logger.info("\n" + "="*60)
    logger.info("测试 3: 空策略（无过滤器）")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "filters": []
    }
    
    logger.info(f"策略配置: {strategy_config}")
    
    result = run_scan_job(strategy_config, stocks, scan_date)
    
    logger.info(f"筛选结果: {len(result)} 只股票 (应等于输入数量)")


def test_default_params():
    """测试使用默认参数"""
    logger.info("\n" + "="*60)
    logger.info("测试 4: 使用默认参数")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "filters": [
            {
                "type": "change_percent",
                "params": {}
            }
        ]
    }
    
    logger.info(f"策略配置: {strategy_config}")
    logger.info("(使用默认参数: min_change=3.0, max_change=6.0)")
    
    result = run_scan_job(strategy_config, stocks, scan_date)
    
    logger.info(f"筛选结果: {len(result)} 只股票")


def test_get_registered_filters():
    """测试获取已注册的过滤器列表"""
    logger.info("\n" + "="*60)
    logger.info("测试 5: 获取已注册的过滤器")
    logger.info("="*60)
    
    scan_job = get_scan_job()
    filters = scan_job.get_registered_filters()
    
    logger.info(f"已注册的过滤器: {filters}")


if __name__ == "__main__":
    test_get_registered_filters()
    test_empty_strategy()
    test_default_params()
    test_single_filter()
    test_complete_json_strategy()
    
    logger.info("\n" + "="*60)
    logger.info("所有测试完成！")
    logger.info("="*60)
