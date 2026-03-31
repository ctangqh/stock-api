from datetime import date
import logging
from strategy.conditions import (
    ChangePercentCondition,
    MarketCapCondition,
    MACondition,
    AndCompositeCondition,
    OrCompositeCondition,
    Operator
)

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
    """创建模拟上下文数据（包含技术指标）"""
    return {
        'stock_latest_indicator': {
            '000001': {'ma5': 12.0, 'ma10': 11.8, 'ma20': 11.5, 'ma60': 10.8},
            '000002': {'ma5': 8.0, 'ma10': 7.9, 'ma20': 7.8, 'ma60': 7.5},
            '600000': {'ma5': 9.5, 'ma10': 9.3, 'ma20': 9.0, 'ma60': 8.7}
        },
        'stock_market_caps': {
            '000001': 250.0,
            '000002': 320.0,
            '600000': 280.0
        }
    }


def test_change_percent_single_condition():
    """测试单个涨跌幅条件"""
    logger.info("\n" + "="*60)
    logger.info("测试 1: 单个涨跌幅条件 (change_percent >= 3.0")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    scan_date = date(2026, 3, 30)
    context = create_mock_context()
    
    # 创建条件：涨跌幅 >= 3.0
    condition = ChangePercentCondition(Operator.GREATER_OR_EQUAL, 3.0)
    
    logger.info(f"条件: change_percent {condition.operator.value} {condition.target_value}")
    
    result = []
    for stock in stocks:
        if condition.evaluate(stock['code'], stock, scan_date, context):
            result.append(stock)
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']} (涨跌幅: {stock['change_percent']}%)")


def test_change_percent_range_with_and():
    """测试使用 AND 组合多个涨跌幅条件（范围）"""
    logger.info("\n" + "="*60)
    logger.info("测试 2: 组合涨跌幅条件 (3.0 <= change_percent <= 6.0 (AND)")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    scan_date = date(2026, 3, 30)
    context = create_mock_context()
    
    # 创建两个条件并使用 AND 组合
    cond1 = ChangePercentCondition(Operator.GREATER_OR_EQUAL, 3.0)
    cond2 = ChangePercentCondition(Operator.LESS_OR_EQUAL, 6.0)
    and_condition = AndCompositeCondition([cond1, cond2])
    
    logger.info(f"条件: (change_percent >= 3.0) AND (change_percent <= 6.0)")
    
    result = []
    for stock in stocks:
        if and_condition.evaluate(stock['code'], stock, scan_date, context):
            result.append(stock)
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']} (涨跌幅: {stock['change_percent']}%)")


def test_market_cap_single_condition():
    """测试单个市值条件"""
    logger.info("\n" + "="*60)
    logger.info("测试 3: 单个市值条件 (market_cap >= 200.0")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    scan_date = date(2026, 3, 30)
    context = create_mock_context()
    
    condition = MarketCapCondition(Operator.GREATER_OR_EQUAL, 200.0)
    
    logger.info(f"条件: market_cap {condition.operator.value} {condition.target_value} 亿元")
    
    result = []
    for stock in stocks:
        if condition.evaluate(stock['code'], stock, scan_date, context):
            result.append(stock)
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        market_cap = stock['market_value'] / 100000000.0
        logger.info(f"  - {stock['code']} {stock['name']} (市值: {market_cap} 亿元)")


def test_ma_single_condition():
    """测试单个均线条件"""
    logger.info("\n" + "="*60)
    logger.info("测试 4: 单个均线条件 (收盘价 >= MA20")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    scan_date = date(2026, 3, 30)
    context = create_mock_context()
    
    condition = MACondition(ma_period=20, operator=Operator.LESS_OR_EQUAL)
    
    logger.info(f"条件: 收盘价 >= MA{condition.ma_period} (MA {condition.operator.value} 收盘价)")
    
    result = []
    for stock in stocks:
        if condition.evaluate(stock['code'], stock, scan_date, context):
            result.append(stock)
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        ma20 = context['stock_latest_indicator'][stock['code']]['ma20']
        logger.info(f"  - {stock['code']} {stock['name']} (收盘价: {stock['close']}, MA20: {ma20})")


def test_combined_all_filters():
    """测试多个不同类型条件的组合"""
    logger.info("\n" + "="*60)
    logger.info("测试 5: 组合所有类型条件 (涨跌幅、市值、均线 (AND)")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    scan_date = date(2026, 3, 30)
    context = create_mock_context()
    
    # 构建组合条件
    cond1 = ChangePercentCondition(Operator.GREATER_OR_EQUAL, 3.0)
    cond2 = ChangePercentCondition(Operator.LESS_OR_EQUAL, 6.0)
    cond3 = MarketCapCondition(Operator.GREATER_OR_EQUAL, 200.0)
    cond4 = MarketCapCondition(Operator.LESS_OR_EQUAL, 350.0)
    cond5 = MACondition(ma_period=20, operator=Operator.LESS_OR_EQUAL)
    
    and_condition = AndCompositeCondition([cond1, cond2, cond3, cond4, cond5])
    
    logger.info(f"组合条件: (涨跌幅 3~6) AND (市值 200~350亿) AND (收盘价 >= MA20)")
    
    result = []
    for stock in stocks:
        if and_condition.evaluate(stock['code'], stock, scan_date, context):
            result.append(stock)
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']}")


def test_or_condition():
    """测试 OR 组合条件"""
    logger.info("\n" + "="*60)
    logger.info("测试 6: OR 组合条件 (涨跌幅 >=5 OR 市值 >=300亿)")
    logger.info("="*60)
    
    stocks = create_mock_stocks()
    scan_date = date(2026, 3, 30)
    context = create_mock_context()
    
    cond1 = ChangePercentCondition(Operator.GREATER_OR_EQUAL, 5.0)
    cond2 = MarketCapCondition(Operator.GREATER_OR_EQUAL, 300.0)
    or_condition = OrCompositeCondition([cond1, cond2])
    
    logger.info(f"条件: (涨跌幅 >= 5.0) OR (市值 >= 300亿)")
    
    result = []
    for stock in stocks:
        if or_condition.evaluate(stock['code'], stock, scan_date, context):
            result.append(stock)
    
    logger.info(f"筛选结果: {len(result)} 只股票")
    for stock in result:
        logger.info(f"  - {stock['code']} {stock['name']}")


def test_condition_serialization():
    """测试条件的序列化和反序列化"""
    logger.info("\n" + "="*60)
    logger.info("测试 7: 条件序列化和反序列化")
    logger.info("="*60)
    
    # 测试 ChangePercentCondition
    cond1 = ChangePercentCondition(Operator.GREATER_OR_EQUAL, 3.0)
    dict1 = cond1.to_dict()
    logger.info(f"ChangePercentCondition 序列化: {dict1}")
    cond1_restored = ChangePercentCondition.from_dict(dict1)
    logger.info(f"ChangePercentCondition 反序列化成功")
    
    # 测试 MarketCapCondition
    cond2 = MarketCapCondition(Operator.LESS_OR_EQUAL, 800.0)
    dict2 = cond2.to_dict()
    logger.info(f"MarketCapCondition 序列化: {dict2}")
    cond2_restored = MarketCapCondition.from_dict(dict2)
    logger.info(f"MarketCapCondition 反序列化成功")
    
    # 测试 MACondition
    cond3 = MACondition(ma_period=20, operator=Operator.GREATER_THAN)
    dict3 = cond3.to_dict()
    logger.info(f"MACondition 序列化: {dict3}")
    cond3_restored = MACondition.from_dict(dict3)
    logger.info(f"MACondition 反序列化成功")
    
    # 测试组合条件
    and_cond = AndCompositeCondition([cond1, cond2])
    dict_and = and_cond.to_dict()
    logger.info(f"AndCompositeCondition 序列化: {dict_and}")
    and_cond_restored = AndCompositeCondition.from_dict(dict_and)
    logger.info(f"AndCompositeCondition 反序列化成功")


if __name__ == "__main__":
    test_condition_serialization()
    test_change_percent_single_condition()
    test_change_percent_range_with_and()
    test_market_cap_single_condition()
    test_ma_single_condition()
    test_or_condition()
    test_combined_all_filters()
    
    logger.info("\n" + "="*60)
    logger.info("所有测试完成！")
    logger.info("="*60)
