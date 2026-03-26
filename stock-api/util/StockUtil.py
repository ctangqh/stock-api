import logging
from datetime import date, timedelta
from typing import List, Dict, Optional
import pandas as pd

from data.stock_cn_history_market import StockCnHistoryMarketORM
from util.TechnicalAnalysis import calculate_sma, calculate_macd
from conf.Config import DB_CONFIG

logger = logging.getLogger(__name__)


def get_stock_technical_indicators(
    stock_code: str,
    target_date: date,
    days_back: int = 60
) -> List[Dict]:
    """
    获取股票技术指标数据
    
    :param stock_code: 股票代码
    :param target_date: 目标日期
    :param days_back: 回溯天数，默认60天
    :return: 包含技术指标的股票数据列表
    """
    logger.info(f"获取 {stock_code} 在 {target_date} 的技术指标，回溯 {days_back} 天")
    
    # 计算开始日期
    start_date = target_date - timedelta(days=days_back)
    
    # 查询历史数据
    stock_orm = StockCnHistoryMarketORM(DB_CONFIG)
    history_data = stock_orm.get_by_code_and_date_range(stock_code, start_date, target_date)
    
    if not history_data:
        logger.warning(f"未找到 {stock_code} 在 {start_date} 到 {target_date} 的历史数据")
        return []
    
    # 转换为 DataFrame 以便计算指标
    df = pd.DataFrame(history_data)
    df = df.sort_values('data_date').reset_index(drop=True)
    
    # 提取收盘价序列
    close_prices = df['close']
    
    # 计算均线
    ma_periods = [5, 10, 20, 60]
    ma_data = {}
    for period in ma_periods:
        ma_series = calculate_sma(close_prices, period)
        ma_data[f'ma{period}'] = ma_series
    
    # 计算 MACD
    macd_data = calculate_macd(close_prices)
    
    # 合并指标到原始数据
    result = []
    for idx, row in df.iterrows():
        record = row.to_dict()
        
        # 添加均线数据，处理 NaN
        for period in ma_periods:
            ma_value = ma_data[f'ma{period}'].iloc[idx]
            record[f'ma{period}'] = float(ma_value) if pd.notna(ma_value) else None
        
        # 添加 MACD 数据，处理 NaN
        record['macd_dif'] = float(macd_data['dif'].iloc[idx]) if pd.notna(macd_data['dif'].iloc[idx]) else None
        record['macd_dea'] = float(macd_data['dea'].iloc[idx]) if pd.notna(macd_data['dea'].iloc[idx]) else None
        record['macd_hist'] = float(macd_data['macd_hist'].iloc[idx]) if pd.notna(macd_data['macd_hist'].iloc[idx]) else None
        
        result.append(record)
    
    logger.info(f"成功计算 {stock_code} 的技术指标，共 {len(result)} 条记录")
    return result


def batch_get_stock_indicators(
    stock_codes: List[str],
    target_date: date,
    days_back: int = 60
) -> Dict[str, List[Dict]]:
    """
    批量获取多只股票的技术指标数据
    
    :param stock_codes: 股票代码列表
    :param target_date: 目标日期
    :param days_back: 回溯天数，默认60天
    :return: 字典，key 为股票代码，value 为该股票的技术指标数据列表
    """
    logger.info(f"批量获取 {len(stock_codes)} 只股票的技术指标")
    
    result = {}
    for code in stock_codes:
        try:
            result[code] = get_stock_technical_indicators(code, target_date, days_back)
        except Exception as e:
            logger.error(f"获取 {code} 的技术指标失败: {e}")
            result[code] = []
    
    return result


def get_latest_stock_indicators(
    stock_code: str,
    days: int = 60
) -> List[Dict]:
    """
    获取股票最新的技术指标数据（使用今天作为目标日期）
    
    :param stock_code: 股票代码
    :param days: 回溯天数，默认60天
    :return: 包含技术指标的股票数据列表
    """
    today = date.today()
    return get_stock_technical_indicators(stock_code, today, days)


def fetch_stock_indicators(
    filtered: List[Dict], 
    scan_date: date, 
    days_back: int = 60
) -> tuple[Dict[str, List[Dict]], Dict[str, Dict]]:
    """
    从筛选后的股票列表获取技术指标
    
    :param filtered: 筛选后的股票列表
    :param scan_date: 选股日期
    :param days_back: 回溯天数，默认60天
    :return: (stock_indicators, stock_latest_indicator) 元组
    """
    stock_codes = [d['code'] for d in filtered]
    stock_indicators: Dict[str, List[Dict]] = {}
    if stock_codes:
        stock_indicators = batch_get_stock_indicators(stock_codes, scan_date, days_back=days_back)
    
    stock_latest_indicator = {}
    for code, indicators in stock_indicators.items():
        if indicators:
            stock_latest_indicator[code] = indicators[-1]
    
    return stock_indicators, stock_latest_indicator
