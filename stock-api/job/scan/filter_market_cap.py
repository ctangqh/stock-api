from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def filter_market_cap(
    stocks: List[Dict[str, Any]],
    stock_market_caps: Dict[str, float],
    min_cap: float = 60.0,
    max_cap: float = 800.0
) -> List[Dict[str, Any]]:
    if not stocks:
        logger.warning("输入股票列表为空，市值筛选返回空")
        return []
    
    if not stock_market_caps:
        logger.warning("市值数据为空，市值筛选返回空")
        return []
    
    filtered = []
    skipped_count = 0
    
    for stock in stocks:
        code = stock.get('code')
        
        if code not in stock_market_caps:
            skipped_count += 1
            continue
        
        market_cap = stock_market_caps[code]
        
        if min_cap <= market_cap <= max_cap:
            filtered.append(stock)
    
    logger.info(
        f"市值筛选完成: 输入 {len(stocks)} 只, "
        f"输出 {len(filtered)} 只, "
        f"跳过无市值数据 {skipped_count} 只"
    )
    
    return filtered
