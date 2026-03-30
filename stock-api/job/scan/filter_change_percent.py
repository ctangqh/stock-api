"""
涨跌幅筛选函数
基于涨跌幅范围筛选股票
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def filter_change_percent(
    stocks: List[Dict[str, Any]],
    min_change: float = 3.0,
    max_change: float = 6.0
) -> List[Dict[str, Any]]:
    """
    按涨跌幅范围筛选股票
    
    参数:
        stocks: 股票列表，每个元素为字典，需包含 'change_percent' 字段
        min_change: 最小涨跌幅（%），默认 3.0
        max_change: 最大涨跌幅（%），默认 6.0
    
    返回:
        符合涨跌幅条件的股票列表
    """
    if not stocks:
        logger.warning("输入股票列表为空，涨跌幅筛选返回空")
        return []
    
    filtered = []
    skipped_count = 0
    
    for stock in stocks:
        change_percent = stock.get('change_percent')
        
        if change_percent is None:
            skipped_count += 1
            continue
        
        if min_change <= change_percent <= max_change:
            filtered.append(stock)
    
    logger.info(
        f"涨跌幅筛选完成: 输入 {len(stocks)} 只, "
        f"输出 {len(filtered)} 只, "
        f"跳过无涨跌幅数据 {skipped_count} 只"
    )
    
    return filtered
