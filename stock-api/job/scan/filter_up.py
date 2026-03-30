from typing import List, Dict, Any
from datetime import date, timedelta
import logging

from data.stock_cn_history_market import StockCnHistoryMarketORM
from conf.Config import DB_CONFIG

logger = logging.getLogger(__name__)


def filter_up(
    stocks: List[Dict[str, Any]],
    consecutive_days: int = 3,
    scan_date: date = None
) -> List[Dict[str, Any]]:
    if not stocks:
        logger.warning("输入股票列表为空，连续上涨筛选返回空")
        return []
    
    if scan_date is None:
        scan_date = date.today()
    
    filtered = []
    skipped_count = 0
    
    market_orm = StockCnHistoryMarketORM(DB_CONFIG)
    
    try:
        for stock in stocks:
            code = stock.get('code')
            
            if not code:
                skipped_count += 1
                continue
            
            if _check_consecutive_up(market_orm, code, consecutive_days, scan_date):
                filtered.append(stock)
    
    finally:
        market_orm.close()
    
    logger.info(
        f"连续上涨筛选完成: 输入 {len(stocks)} 只, "
        f"输出 {len(filtered)} 只, "
        f"跳过无代码 {skipped_count} 只"
    )
    
    return filtered


def _check_consecutive_up(
    market_orm: StockCnHistoryMarketORM,
    stock_code: str,
    consecutive_days: int,
    scan_date: date
) -> bool:
    try:
        days_back = consecutive_days + 10
        start_date = scan_date - timedelta(days=days_back)
        
        history = market_orm.get_by_code_and_date_range(
            stock_code, 
            start_date, 
            scan_date
        )
        
        if not history:
            logger.debug(f"股票 {stock_code} 无历史数据")
            return False
        
        sorted_history = sorted(history, key=lambda x: x['data_date'], reverse=True)
        
        recent_history = sorted_history[:consecutive_days]
        
        if len(recent_history) < consecutive_days:
            logger.debug(f"股票 {stock_code} 历史数据不足 {consecutive_days} 天")
            return False
        
        for record in recent_history:
            change_percent = record.get('change_percent')
            
            if change_percent is None:
                logger.debug(f"股票 {stock_code} 某日无涨跌幅数据")
                return False
            
            if change_percent <= 0:
                logger.debug(f"股票 {stock_code} 某日涨跌幅 {change_percent}% 不满足 >0")
                return False
        
        return True
    
    except Exception as e:
        logger.error(f"检查股票 {stock_code} 连续上涨时出错: {e}")
        return False
