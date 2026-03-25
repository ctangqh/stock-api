from data.stock_choose_strategy import StockChooseStrategyORM
from data.stock_best_choose import StockBestChooseORM
from data.stock_cn_history_market import StockCnHistoryMarketORM
from util.TechnicalAnalysis import detect_death_cross
from conf.Config import DB_CONFIG
from datetime import date
import logging
import pandas as pd
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def screen_stocks(date: Optional[date] = None):
    if date is None:
        date = date.today()
    
    logger.info(f"开始股票筛选，日期: {date}")
    
    strategy_orm = StockChooseStrategyORM(DB_CONFIG)
    best_choose_orm = StockBestChooseORM(DB_CONFIG)
    market_orm = StockCnHistoryMarketORM(DB_CONFIG)
    
    try:
        strategies = strategy_orm.get_all_active()
        if not strategies:
            logger.warning("未找到激活状态的策略")
            return
        
        for strategy in strategies:
            strategy_name = strategy['name']
            strategy_value = strategy['value']
            logger.info(f"使用策略: {strategy_name}, 参数: {strategy_value}")
            
            market_data = market_orm.get_by_trade_date(date)
            logger.info(f"获取到 {len(market_data)} 条市场数据")
            
            min_change = strategy_value.get('min_change_rate', 3.0)
            max_change = strategy_value.get('max_change_rate', 6.0)
            filtered = [
                d for d in market_data 
                if d.get('change_rate') is not None 
                and min_change <= d['change_rate'] <= max_change
            ]
            logger.info(f"涨跌幅筛选后剩余 {len(filtered)} 只股票")
            
            if strategy_value.get('check_ma20', True):
                filtered = [
                    d for d in filtered
                    if d.get('close') is not None 
                    and d.get('ma20') is not None
                    and d['close'] > d['ma20']
                ]
                logger.info(f"MA20 筛选后剩余 {len(filtered)} 只股票")
            
            if strategy_value.get('check_macd', True):
                macd_filtered = []
                for stock in filtered:
                    code = stock['code']
                    recent_data = market_orm.get_by_code(code, limit=60)
                    if len(recent_data) < 26:
                        continue
                    
                    df = pd.DataFrame(recent_data)
                    df = df.sort_values('trade_date').reset_index(drop=True)
                    
                    dif = pd.Series(df['macd_dif'])
                    dea = pd.Series(df['macd_dea'])
                    death_crosses = detect_death_cross(dif, dea)
                    
                    if not death_crosses or death_crosses[-1] < len(df) - 10:
                        macd_filtered.append(stock)
                filtered = macd_filtered
                logger.info(f"MACD 筛选后剩余 {len(filtered)} 只股票")
            
            if strategy_value.get('check_recent_rise', True):
                recent_days = strategy_value.get('recent_days', 3)
                rise_filtered = []
                for stock in filtered:
                    code = stock['code']
                    recent_data = market_orm.get_by_code(code, limit=recent_days + 1)
                    if len(recent_data) < recent_days:
                        continue
                    
                    df = pd.DataFrame(recent_data)
                    df = df.sort_values('trade_date').tail(recent_days).reset_index(drop=True)
                    
                    all_rise = True
                    for i in range(len(df)):
                        if df.iloc[i]['change_rate'] is None or df.iloc[i]['change_rate'] <= 0:
                            all_rise = False
                            break
                    if all_rise:
                        rise_filtered.append(stock)
                filtered = rise_filtered
                logger.info(f"近期上涨筛选后剩余 {len(filtered)} 只股票")
            
            if filtered:
                best_choose_list = []
                for stock in filtered:
                    choose_reason = {
                        "strategy": strategy_name,
                        "strategy_params": strategy_value,
                        "scan_date": date.isoformat(),
                        "stock_info": {
                            "code": stock['code'],
                            "name": stock.get('name'),
                            "close": stock['close'],
                            "change_rate": stock['change_rate'],
                            "ma20": stock.get('ma20')
                        }
                    }
                    best_choose_list.append({
                        "code": stock['code'],
                        "name": stock.get('name'),
                        "scan_date": date,
                        "choose_reason": choose_reason
                    })
                best_choose_orm.batch_insert(best_choose_list)
                logger.info(f"成功保存 {len(best_choose_list)} 只股票到选股结果")
    
    except Exception as e:
        logger.exception(f"股票筛选异常: {e}")
    finally:
        strategy_orm.close()
        best_choose_orm.close()
        market_orm.close()
        logger.info("股票筛选结束")


if __name__ == "__main__":
    screen_stocks()
