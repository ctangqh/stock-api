from datetime import date
import logging
from job.scan.run import run_scan_job

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
            'market_value': 25000000000.0  # 250亿元
        },
        {
            'code': '000002',
            'name': '万科A',
            'close': 8.2,
            'change_percent': 2.0,
            'market_value': 32000000000.0  # 320亿元
        },
        {
            'code': '600000',
            'name': '浦发银行',
            'close': 9.8,
            'change_percent': 5.2,
            'market_value': 28000000000.0  # 280亿元
        }
    ]


def create_mock_context():
    """创建模拟上下文数据"""
    return {
        'stock_market_caps': {
            '000001': 250.0,
            '000002': 320.0,
            '600000': 280.0
        },
        'stock_latest_indicator': {
            '000001': {'ma5': 12.0, 'ma10': 11.8, 'ma20': 11.5, 'ma60': 10.8},
            '000002': {'ma5': 8.0, 'ma10': 7.9, 'ma20': 7.8, 'ma60': 7.5},
            '600000': {'ma5': 9.5, 'ma10': 9.3, 'ma20': 9.0, 'ma60': 8.7}
        }
    }


def test_single_change_percent_condition():
    """测试单个涨跌幅条件（新格式）"""
    logger.info("\n" + "="*60)
    logger.info("测试 1: 单个涨跌幅条件 (change_percent >= 3.0)")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    context = create_mock_context()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "type": "change_percent",
        "operator": ">=",
        "target_value": 3.0
    }
    
    logger.info(f"策略配置: {strategy_config}")
    
    result = run_scan_job(
        strategy_config,
        stocks,
        scan_date,
        **context
    )
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']} (涨跌幅: {stock['change_percent']}%)")


def test_change_percent_range_with_and():
    """测试使用 AND 组合多个涨跌幅条件（范围）"""
    logger.info("\n" + "="*60)
    logger.info("测试 2: 组合涨跌幅条件 (3.0 <= change_percent <= 6.0 (AND))")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    context = create_mock_context()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "type": "and",
        "conditions": [
            {
                "type": "change_percent",
                "operator": ">=",
                "target_value": 3.0
            },
            {
                "type": "change_percent",
                "operator": "<=",
                "target_value": 6.0
            }
        ]
    }
    
    logger.info(f"策略配置: {strategy_config}")
    
    result = run_scan_job(
        strategy_config,
        stocks,
        scan_date,
        **context
    )
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']} (涨跌幅: {stock['change_percent']}%)")


def test_market_cap_condition():
    """测试市值条件"""
    logger.info("\n" + "="*60)
    logger.info("测试 3: 市值条件 (market_cap >= 200.0)")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    context = create_mock_context()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "type": "market_cap",
        "operator": ">=",
        "target_value": 200.0
    }
    
    logger.info(f"策略配置: {strategy_config}")
    
    result = run_scan_job(
        strategy_config,
        stocks,
        scan_date,
        **context
    )
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        market_cap = context['stock_market_caps'][stock['code']]
        logger.info(f"  - {stock['code']} {stock['name']} (市值: {market_cap} 亿元)")


def test_ma_condition():
    """测试均线条件"""
    logger.info("\n" + "="*60)
    logger.info("测试 4: 均线条件 (收盘价 >= MA20)")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    context = create_mock_context()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "type": "ma",
        "ma_period": 20,
        "operator": "<="
    }
    
    logger.info(f"策略配置: {strategy_config}")
    logger.info("(MA <= 收盘价 等价于 收盘价 >= MA)")
    
    result = run_scan_job(
        strategy_config,
        stocks,
        scan_date,
        **context
    )
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        ma20 = context['stock_latest_indicator'][stock['code']]['ma20']
        logger.info(f"  - {stock['code']} {stock['name']} (收盘价: {stock['close']}, MA20: {ma20})")


def test_combined_all_conditions():
    """测试所有条件的组合"""
    logger.info("\n" + "="*60)
    logger.info("测试 5: 组合所有类型条件 (涨跌幅、市值、均线 (AND))")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    context = create_mock_context()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "type": "and",
        "conditions": [
            {
                "type": "change_percent",
                "operator": ">=",
                "target_value": 3.0
            },
            {
                "type": "change_percent",
                "operator": "<=",
                "target_value": 6.0
            },
            {
                "type": "market_cap",
                "operator": ">=",
                "target_value": 200.0
            },
            {
                "type": "market_cap",
                "operator": "<=",
                "target_value": 350.0
            },
            {
                "type": "ma",
                "ma_period": 20,
                "operator": "<="
            }
        ]
    }
    
    logger.info(f"策略配置: {strategy_config}")
    logger.info("组合条件: (涨跌幅 3~6) AND (市值 200~350亿) AND (收盘价 >= MA20)")
    
    result = run_scan_job(
        strategy_config,
        stocks,
        scan_date,
        **context
    )
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']}")


def test_or_condition():
    """测试 OR 组合条件"""
    logger.info("\n" + "="*60)
    logger.info("测试 6: OR 组合条件 (涨跌幅 >=5 OR 市值 >=300亿)")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    context = create_mock_context()
    scan_date = date(2026, 3, 30)
    
    strategy_config = {
        "type": "or",
        "conditions": [
            {
                "type": "change_percent",
                "operator": ">=",
                "target_value": 5.0
            },
            {
                "type": "market_cap",
                "operator": ">=",
                "target_value": 300.0
            }
        ]
    }
    
    logger.info(f"策略配置: {strategy_config}")
    
    result = run_scan_job(
        strategy_config,
        stocks,
        scan_date,
        **context
    )
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']}")


if __name__ == "__main__":
    test_single_change_percent_condition()
    test_change_percent_range_with_and()
    test_market_cap_condition()
    test_ma_condition()
    test_or_condition()
    test_combined_all_conditions()
    
    logger.info("\n" + "="*60)
    logger.info("所有测试完成！")
    logger.info("="*60)
