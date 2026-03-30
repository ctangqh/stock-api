from data.stock_choose_strategy import StockChooseStrategyORM
from data.stock_best_choose import StockBestChooseORM
from data.stock_cn_history_market import StockCnHistoryMarketORM
from data.stock_cn_info import StockCnInfoORM
from conf.Config import DB_CONFIG
from datetime import date
import logging
from typing import Optional, List, Dict, Any

from job.scan import apply_all_filters
from util.StockUtil import fetch_stock_indicators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def screen_stocks(scan_date: Optional[date] = None):
    if scan_date is None:
        scan_date = date.today()
    
    logger.info(f"开始股票筛选，日期: {scan_date}")
    
    strategy_orm = StockChooseStrategyORM(DB_CONFIG)
    best_choose_orm = StockBestChooseORM(DB_CONFIG)
    market_orm = StockCnHistoryMarketORM(DB_CONFIG)
    info_orm = StockCnInfoORM(DB_CONFIG)
    
    try:
        strategies = strategy_orm.get_all_active()
        if not strategies:
            logger.warning("未找到激活状态的策略")
            return
        
        for strategy in strategies:
            strategy_name = strategy['name']
            strategy_value = strategy['value']
            logger.info(f"使用策略: {strategy_name}")
            
            selected_stocks = _screen_with_strategy(
                strategy_value,
                scan_date,
                market_orm,
                info_orm
            )
            
            logger.info(f"策略 '{strategy_name}' 选出 {len(selected_stocks)} 只股票")
            
            if not selected_stocks:
                logger.info("未筛选出符合条件的股票")
                continue
            
            stock_indicators, stock_latest_indicator = fetch_stock_indicators(
                selected_stocks, scan_date
            )
            
            save_results(
                selected_stocks, 
                strategy_name, 
                strategy_value, 
                scan_date, 
                stock_latest_indicator, 
                best_choose_orm
            )
    
    except Exception as e:
        logger.exception(f"股票筛选异常: {e}")
    finally:
        strategy_orm.close()
        best_choose_orm.close()
        market_orm.close()
        info_orm.close()
        logger.info("股票筛选结束")


def _screen_with_strategy(
    strategy_config: Dict[str, Any],
    scan_date: date,
    market_orm: StockCnHistoryMarketORM,
    info_orm: StockCnInfoORM
) -> List[Dict[str, Any]]:
    stocks = market_orm.get_by_data_date(scan_date)
    logger.info(f"从数据库获取到 {len(stocks)} 只股票")
    
    if not stocks:
        return []
    
    stock_codes = [s['code'] for s in stocks]
    
    stock_info_map = info_orm.batch_get_by_codes(stock_codes)
    stock_market_caps = {
        code: info.get('market_cap', 0)
        for code, info in stock_info_map.items()
    }
    
    stock_indicators, stock_latest_indicator = fetch_stock_indicators(
        stocks, scan_date, days_back=60
    )
    
    selected_stocks = apply_all_filters(
        stocks,
        stock_market_caps,
        stock_latest_indicator,
        strategy_config,
        scan_date
    )
    
    return selected_stocks


def save_results(filtered, strategy_name, strategy_value, scan_date, 
                 stock_latest_indicator, best_choose_orm):
    if not filtered:
        logger.info("没有符合条件的股票，跳过保存")
        return
    
    best_choose_list = []
    for stock in filtered:
        ma20 = None
        if stock['code'] in stock_latest_indicator:
            ma20 = stock_latest_indicator[stock['code']].get('ma20')
        
        choose_reason = {
            "strategy": strategy_name,
            "strategy_params": strategy_value,
            "scan_date": scan_date.isoformat(),
            "stock_info": {
                "code": stock['code'],
                "name": stock.get('name'),
                "close": stock['close'],
                "change_percent": stock.get('change_percent'),
                "ma20": ma20
            }
        }
        best_choose_list.append({
            "code": stock['code'],
            "name": stock.get('name'),
            "scan_date": scan_date,
            "choose_reason": choose_reason
        })
    best_choose_orm.batch_insert(best_choose_list)
    logger.info(f"成功保存 {len(best_choose_list)} 只股票到选股结果")


if __name__ == "__main__":
    screen_stocks()
