from datetime import date
import logging
from job.scan.run import run_scan_job
from strategy.parser import StrategyParser
from strategy.conditions import Condition

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
            'market_value': 25000000000.0
        },
        {
            'code': '000002',
            'name': '万科A',
            'close': 8.2,
            'change_percent': 2.0,
            'market_value': 32000000000.0
        },
        {
            'code': '600000',
            'name': '浦发银行',
            'close': 9.8,
            'change_percent': 5.2,
            'market_value': 28000000000.0
        },
        {
            'code': '000004',
            'name': '国华网安',
            'close': 15.3,
            'change_percent': 7.8,
            'market_value': 45000000000.0
        },
        {
            'code': '000005',
            'name': '世纪星源',
            'close': 3.2,
            'change_percent': 1.5,
            'market_value': 3000000000.0
        }
    ]


def create_mock_context():
    """创建模拟上下文数据"""
    return {
        'stock_market_caps': {
            '000001': 250.0,
            '000002': 320.0,
            '600000': 280.0,
            '000004': 450.0,
            '000005': 30.0
        },
        'stock_latest_indicator': {
            '000001': {'ma5': 12.0, 'ma10': 11.8, 'ma20': 11.5, 'ma60': 10.8},
            '000002': {'ma5': 8.0, 'ma10': 7.9, 'ma20': 7.8, 'ma60': 7.5},
            '600000': {'ma5': 9.5, 'ma10': 9.3, 'ma20': 9.0, 'ma60': 8.7},
            '000004': {'ma5': 14.5, 'ma10': 14.0, 'ma20': 13.5, 'ma60': 12.0},
            '000005': {'ma5': 3.0, 'ma10': 2.9, 'ma20': 2.8, 'ma60': 2.5}
        }
    }


def print_stock_list(title, stocks):
    """打印股票列表"""
    logger.info(f"\n{title}")
    logger.info(f"{'代码':<10} {'名称':<12} {'涨跌幅(%)':<12} {'市值(亿)':<12} {'收盘价':<10} {'MA20':<10}")
    logger.info("-" * 70)
    for stock in stocks:
        change = f"{stock.get('change_percent', 'N/A'):>6.2f}" if stock.get('change_percent') is not None else "   N/A"
        market_cap = context['stock_market_caps'].get(stock['code'], 'N/A')
        ma20 = context['stock_latest_indicator'].get(stock['code'], {}).get('ma20', 'N/A')
        logger.info(
            f"{stock['code']:<10} "
            f"{stock.get('name', 'N/A'):<12} "
            f"{change:<12} "
            f"{market_cap:<12} "
            f"{stock.get('close', 'N/A'):<10} "
            f"{ma20:<10}"
        )
    logger.info("-" * 70)
    logger.info(f"共 {len(stocks)} 只股票\n")


def test_detailed_strategy():
    """测试详细的策略执行步骤"""
    global context
    
    logger.info("\n" + "="*80)
    logger.info("详细策略执行测试 - 新格式")
    logger.info("="*80)
    
    stocks = create_mock_stocks()
    context = create_mock_context()
    scan_date = date(2026, 3, 30)
    
    # 打印初始股票池
    print_stock_list("初始股票池（全部股票）：", stocks)
    
    # 策略配置
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
    
    logger.info(f"策略配置：")
    import json
    logger.info(json.dumps(strategy_config, indent=2, ensure_ascii=False))
    
    # 逐步评估每个条件
    logger.info("\n" + "="*80)
    logger.info("逐步执行策略条件：")
    logger.info("="*80)
    
    current_stocks = stocks.copy()
    
    # 我们手动逐个应用条件，以便详细打印每一步
    conditions_list = strategy_config['conditions']
    
    for i, cond_config in enumerate(conditions_list, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"第 {i} 步：应用条件 {cond_config['type']}")
        logger.info(f"{'='*80}")
        
        # 打印条件描述
        if cond_config['type'] == 'change_percent':
            logger.info(f"条件：涨跌幅 {cond_config['operator']} {cond_config['target_value']}%")
        elif cond_config['type'] == 'market_cap':
            logger.info(f"条件：市值 {cond_config['operator']} {cond_config['target_value']} 亿元")
        elif cond_config['type'] == 'ma':
            logger.info(f"条件：收盘价 >= MA{cond_config['ma_period']} (MA{cond_config['ma_period']} {cond_config['operator']} 收盘价)")
        
        # 解析并应用这个单一条件
        single_condition_strategy = cond_config
        result = run_scan_job(
            single_condition_strategy,
            current_stocks,
            scan_date,
            **context
        )
        
        # 打印过滤掉的股票
        filtered_out = [s for s in current_stocks if s not in result]
        if filtered_out:
            logger.info(f"\n❌ 被过滤掉的股票：")
            print_stock_list("  被过滤股票：", filtered_out)
        
        # 打印保留的股票
        logger.info(f"\n✅ 保留的股票：")
        print_stock_list("  保留股票：", result)
        
        current_stocks = result
        
        if not current_stocks:
            logger.info(f"\n⚠️  无股票剩余，提前结束")
            break
    
    # 最终结果
    logger.info("\n" + "="*80)
    logger.info("最终筛选结果：")
    logger.info("="*80)
    print_stock_list("最终符合条件的股票：", current_stocks)
    
    logger.info("\n" + "="*80)
    logger.info(f"测试完成！共筛选出 {len(current_stocks)} 只股票")
    logger.info("="*80)


if __name__ == "__main__":
    test_detailed_strategy()
