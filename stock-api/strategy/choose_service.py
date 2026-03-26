from datetime import date
import logging
import pandas as pd
from typing import Optional, Dict, List

from util.TechnicalAnalysis import detect_death_cross

logger = logging.getLogger(__name__)


def filter_by_change_percent(market_data: List[Dict], min_change: float = 3.0, max_change: float = 6.0) -> List[Dict]:
    filtered = [
        d for d in market_data 
        if d.get('change_percent') is not None 
        and min_change <= d['change_percent'] <= max_change
    ]
    logger.info(f"涨跌幅筛选 ({min_change}% ~ {max_change}%): {len(market_data)} -> {len(filtered)} 只股票")
    return filtered


def filter_by_ma(filtered: List[Dict], stock_latest_indicator: Dict[str, Dict], ma_period: int = 20) -> List[Dict]:
    if ma_period not in [5, 10, 20, 30, 60]:
        logger.warning(f"不支持的MA周期: {ma_period}，使用默认值20")
        ma_period = 20
    
    ma_key = f'ma{ma_period}'
    new_filtered = []
    
    filtered_map = {d['code']: d for d in filtered}
    
    for code in stock_latest_indicator:
        if code not in filtered_map:
            continue
        
        stock_data = filtered_map[code]
        latest = stock_latest_indicator[code]
        
        if (stock_data.get('close') is not None 
            and latest.get(ma_key) is not None
            and latest[ma_key] < stock_data['close']):
            new_filtered.append(stock_data)
    
    logger.info(f"MA{ma_period} 筛选: {len(filtered)} -> {len(new_filtered)} 只股票")
    return new_filtered


def filter_by_macd(filtered: List[Dict], stock_indicators: Dict[str, List[Dict]]) -> List[Dict]:
    macd_filtered = []
    
    filtered_map = {d['code']: d for d in filtered}
    
    for code in stock_indicators:
        if code not in filtered_map:
            continue
        
        if len(stock_indicators[code]) < 26:
            continue
        
        stock_data = filtered_map[code]
        indicator_data = stock_indicators[code]
        df = pd.DataFrame(indicator_data)
        df = df.sort_values('data_date').reset_index(drop=True)
        
        dif = pd.Series(df['macd_dif'])
        dea = pd.Series(df['macd_dea'])
        death_crosses = detect_death_cross(dif, dea)
        
        if not death_crosses or death_crosses[-1] < len(df) - 10:
            macd_filtered.append(stock_data)
    
    logger.info(f"MACD 筛选: {len(filtered)} -> {len(macd_filtered)} 只股票")
    return macd_filtered


def filter_by_recent_rise(filtered: List[Dict], market_orm, scan_date: date, recent_days: int = 3) -> List[Dict]:
    rise_filtered = []
    for stock in filtered:
        code = stock['code']
        recent_data = market_orm.get_by_code(code, limit=recent_days + 1)
        if len(recent_data) < recent_days:
            continue
        
        df = pd.DataFrame(recent_data)
        df = df.sort_values('data_date').tail(recent_days).reset_index(drop=True)
        
        all_rise = True
        for i in range(len(df)):
            if df.iloc[i]['change_percent'] is None or df.iloc[i]['change_percent'] <= 0:
                all_rise = False
                break
        if all_rise:
            rise_filtered.append(stock)
    logger.info(f"近期上涨筛选 ({recent_days}天): {len(filtered)} -> {len(rise_filtered)} 只股票")
    return rise_filtered


def save_filtered_results(filtered: List[Dict], strategy_name: str, strategy_value: Dict, 
                          scan_date: date, stock_latest_indicator: Dict[str, Dict], 
                          best_choose_orm) -> None:
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
                "change_percent": stock['change_percent'],
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

