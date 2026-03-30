from typing import List, Dict, Any, Optional
from datetime import date
import logging

from .filter_change_percent import filter_change_percent
from .filter_market_cap import filter_market_cap
from .filter_ma import filter_ma, Operator
from .filter_up import filter_up

logger = logging.getLogger(__name__)


def apply_all_filters(
    stocks: List[Dict[str, Any]],
    stock_market_caps: Dict[str, float],
    stock_latest_indicator: Dict[str, Dict[str, Any]],
    strategy_config: Dict[str, Any],
    scan_date: date
) -> List[Dict[str, Any]]:
    logger.info(f"开始应用所有筛选条件，日期: {scan_date}")
    
    change_percent_config = _extract_condition(strategy_config, 'change_percent')
    if change_percent_config:
        stocks = filter_change_percent(
            stocks,
            min_change=change_percent_config.get('min_change', 3.0),
            max_change=change_percent_config.get('max_change', 6.0)
        )
    
    if not stocks:
        logger.info("涨跌幅筛选后无股票，提前结束")
        return []
    
    market_cap_config = _extract_condition(strategy_config, 'market_cap')
    if market_cap_config:
        stocks = filter_market_cap(
            stocks,
            stock_market_caps,
            min_cap=market_cap_config.get('min_cap', 60.0),
            max_cap=market_cap_config.get('max_cap', 800.0)
        )
    
    if not stocks:
        logger.info("市值筛选后无股票，提前结束")
        return []
    
    up_config = _extract_condition(strategy_config, 'continuous_up')
    if up_config:
        stocks = filter_up(
            stocks,
            consecutive_days=up_config.get('days', 3),
            scan_date=scan_date
        )
    
    if not stocks:
        logger.info("连续上涨筛选后无股票，提前结束")
        return []
    
    ma_config = _extract_condition(strategy_config, 'ma')
    if ma_config:
        operator_str = ma_config.get('operator', '>=')
        operator = Operator(operator_str) if operator_str else Operator.GREATER_OR_EQUAL
        stocks = filter_ma(
            stocks,
            stock_latest_indicator,
            ma_period=ma_config.get('ma_period', 20),
            operator=operator
        )
    
    logger.info(f"所有筛选完成，最终结果: {len(stocks)} 只股票")
    return stocks


def _extract_condition(
    strategy_config: Dict[str, Any],
    condition_type: str
) -> Optional[Dict[str, Any]]:
    if strategy_config.get('type') == 'and' or strategy_config.get('type') == 'or':
        conditions = strategy_config.get('conditions', [])
        for cond in conditions:
            if cond.get('type') == condition_type:
                return cond
            nested = _extract_condition(cond, condition_type)
            if nested:
                return nested
    elif strategy_config.get('type') == condition_type:
        return strategy_config
    return None
