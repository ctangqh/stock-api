from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Operator(Enum):
    GREATER_THAN = ">"
    GREATER_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_OR_EQUAL = "<="


def filter_ma(
    stocks: List[Dict[str, Any]],
    stock_latest_indicator: Dict[str, Dict[str, Any]],
    ma_period: int = 20,
    operator: Operator = Operator.GREATER_OR_EQUAL
) -> List[Dict[str, Any]]:
    if not stocks:
        logger.warning("输入股票列表为空，均线筛选返回空")
        return []
    
    if not stock_latest_indicator:
        logger.warning("技术指标数据为空，均线筛选返回空")
        return []
    
    filtered = []
    skipped_count = 0
    
    ma_key = f'ma{ma_period}'
    
    for stock in stocks:
        code = stock.get('code')
        
        if code not in stock_latest_indicator:
            skipped_count += 1
            continue
        
        indicator = stock_latest_indicator[code]
        ma_value = indicator.get(ma_key)
        close_price = stock.get('close')
        
        if ma_value is None or close_price is None:
            skipped_count += 1
            continue
        
        if _compare(close_price, operator, ma_value):
            filtered.append(stock)
    
    logger.info(
        f"均线筛选完成: 输入 {len(stocks)} 只, "
        f"输出 {len(filtered)} 只, "
        f"跳过无数据 {skipped_count} 只"
    )
    
    return filtered


def _compare(value1: float, operator: Operator, value2: float) -> bool:
    if operator == Operator.GREATER_THAN:
        return value1 > value2
    elif operator == Operator.GREATER_OR_EQUAL:
        return value1 >= value2
    elif operator == Operator.LESS_THAN:
        return value1 < value2
    elif operator == Operator.LESS_OR_EQUAL:
        return value1 <= value2
    return False
