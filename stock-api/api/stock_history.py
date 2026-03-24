import logging
import re
from datetime import date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from conf.Config import TECHNICAL_CONFIG, DB_CONFIG
from data.stock_cn_history_market import StockCnHistoryMarketORM
from util.TechnicalAnalysis import (
    calculate_sma,
    calculate_macd,
    detect_golden_cross,
    detect_death_cross,
    detect_bullish_arrangement,
    macd_signal_analysis
)

router = APIRouter(prefix="/api/stock", tags=["stock_history"])
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 正则表达式验证股票代码格式
CODE_PATTERN = re.compile(r'^\d{6}\.(SH|SZ)$')


@router.get("/history/{code}")
async def get_stock_history(
    code: str,
    start_date: Optional[str] = Query(None, description="开始日期，格式 yyyy-mm-dd"),
    end_date: Optional[str] = Query(None, description="结束日期，格式 yyyy-mm-dd"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数，默认 100，最大 1000")
) -> List[Dict[str, Any]]:
    """
    获取股票历史行情数据
    
    参数:
        code: 股票代码，格式为 6位数字.(SH|SZ)
        start_date: 可选，开始日期，格式 yyyy-mm-dd
        end_date: 可选，结束日期，格式 yyyy-mm-dd
        limit: 可选，返回记录数，默认 100，最大 1000
        
    返回:
        按日期升序排列的历史行情数据列表
    """
    try:
        logger.info(f"开始处理 get_stock_history 请求，code={code}, start_date={start_date}, end_date={end_date}, limit={limit}")
        
        # 验证股票代码格式
        if not CODE_PATTERN.match(code):
            raise HTTPException(status_code=400, detail="股票代码格式不正确，应为 6位数字.(SH|SZ)，例如 000001.SZ")
        
        # 验证 limit
        if limit > 1000:
            raise HTTPException(status_code=400, detail="limit 参数不能超过 1000")
        
        with StockCnHistoryMarketORM(DB_CONFIG) as orm:
            if start_date and end_date:
                # 解析日期
                try:
                    start = date.fromisoformat(start_date)
                    end = date.fromisoformat(end_date)
                except ValueError:
                    raise HTTPException(status_code=400, detail="日期格式不正确，应为 yyyy-mm-dd")
                
                records = orm.get_by_code_and_date_range(code, start, end)
                # 按日期升序排列
                records = records[:limit]
            else:
                # 获取最近 limit 条数据（注意 get_by_code 返回的是降序）
                records = orm.get_by_code(code, limit=limit)
                # 反转成升序
                records = list(reversed(records))
        
        logger.info(f"get_stock_history 请求处理成功，返回 {len(records)} 条记录")
        return records
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"处理 get_stock_history 请求失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/indicators/{code}")
async def get_stock_indicators(
    code: str,
    days: int = Query(250, ge=1, description="获取数据的天数，默认 250")
) -> Dict[str, Any]:
    """
    获取股票技术指标（均线和 MACD）
    
    参数:
        code: 股票代码，格式为 6位数字.(SH|SZ)
        days: 可选，获取数据的天数，默认 250
        
    返回:
        包含均线和 MACD 指标的字典
    """
    try:
        logger.info(f"开始处理 get_stock_indicators 请求，code={code}, days={days}")
        
        # 验证股票代码格式
        if not CODE_PATTERN.match(code):
            raise HTTPException(status_code=400, detail="股票代码格式不正确，应为 6位数字.(SH|SZ)，例如 000001.SZ")
        
        # 验证 days
        if days <= 0:
            raise HTTPException(status_code=400, detail="days 参数必须大于 0")
        
        with StockCnHistoryMarketORM(DB_CONFIG) as orm:
            # 获取历史数据（降序）
            records = orm.get_by_code(code, limit=days)
            # 反转成升序
            records = list(reversed(records))
        
        if not records:
            raise HTTPException(status_code=404, detail="未找到该股票的历史数据")
        
        # 转换为 DataFrame
        df = pd.DataFrame(records)
        close_prices = df['close']
        
        # 计算均线
        ma5 = calculate_sma(close_prices, 5)
        ma10 = calculate_sma(close_prices, 10)
        ma20 = calculate_sma(close_prices, 20)
        ma60 = calculate_sma(close_prices, 60)
        
        # 计算 MACD
        macd_result = calculate_macd(close_prices)
        
        # 准备返回数据
        result = {
            "code": code,
            "dates": df['trade_date'].tolist(),
            "ma5": ma5.tolist(),
            "ma10": ma10.tolist(),
            "ma20": ma20.tolist(),
            "ma60": ma60.tolist(),
            "macd_dif": macd_result['dif'].tolist(),
            "macd_dea": macd_result['dea'].tolist(),
            "macd_hist": macd_result['macd_hist'].tolist()
        }
        
        logger.info(f"get_stock_indicators 请求处理成功")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"处理 get_stock_indicators 请求失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/pattern/{code}")
async def get_stock_patterns(
    code: str,
    days: int = Query(60, ge=1, description="获取数据的天数，默认 60")
) -> Dict[str, Any]:
    """
    获取股票形态信号（金叉、死叉、多头排列、MACD 信号等）
    
    参数:
        code: 股票代码，格式为 6位数字.(SH|SZ)
        days: 可选，获取数据的天数，默认 60
        
    返回:
        包含所有形态信号的字典，以及最新日期的状态
    """
    try:
        logger.info(f"开始处理 get_stock_patterns 请求，code={code}, days={days}")
        
        # 验证股票代码格式
        if not CODE_PATTERN.match(code):
            raise HTTPException(status_code=400, detail="股票代码格式不正确，应为 6位数字.(SH|SZ)，例如 000001.SZ")
        
        # 验证 days
        if days <= 0:
            raise HTTPException(status_code=400, detail="days 参数必须大于 0")
        
        with StockCnHistoryMarketORM(DB_CONFIG) as orm:
            # 获取历史数据（降序）
            records = orm.get_by_code(code, limit=days)
            # 反转成升序
            records = list(reversed(records))
        
        if not records:
            raise HTTPException(status_code=404, detail="未找到该股票的历史数据")
        
        # 转换为 DataFrame
        df = pd.DataFrame(records)
        close_prices = df['close']
        
        # 计算均线
        ma5 = calculate_sma(close_prices, 5)
        ma10 = calculate_sma(close_prices, 10)
        ma20 = calculate_sma(close_prices, 20)
        ma60 = calculate_sma(close_prices, 60)
        
        # 计算 MACD
        macd_result = calculate_macd(close_prices)
        
        # 检测形态
        golden_crosses = detect_golden_cross(ma5, ma20)
        death_crosses = detect_death_cross(ma5, ma20)
        bullish_arrangements = detect_bullish_arrangement(ma5, ma10, ma20, ma60)
        macd_signals = macd_signal_analysis(macd_result['dif'], macd_result['dea'], macd_result['macd_hist'])
        
        # 获取最新日期的状态
        latest_idx = len(df) - 1
        latest_date = df['trade_date'].iloc[latest_idx]
        
        latest_state = {
            "date": latest_date,
            "ma5": ma5.iloc[latest_idx] if not pd.isna(ma5.iloc[latest_idx]) else None,
            "ma10": ma10.iloc[latest_idx] if not pd.isna(ma10.iloc[latest_idx]) else None,
            "ma20": ma20.iloc[latest_idx] if not pd.isna(ma20.iloc[latest_idx]) else None,
            "ma60": ma60.iloc[latest_idx] if not pd.isna(ma60.iloc[latest_idx]) else None,
            "is_bullish_arrangement": latest_idx in bullish_arrangements,
            "macd_dif": macd_result['dif'].iloc[latest_idx] if not pd.isna(macd_result['dif'].iloc[latest_idx]) else None,
            "macd_dea": macd_result['dea'].iloc[latest_idx] if not pd.isna(macd_result['dea'].iloc[latest_idx]) else None,
            "macd_hist": macd_result['macd_hist'].iloc[latest_idx] if not pd.isna(macd_result['macd_hist'].iloc[latest_idx]) else None
        }
        
        # 准备返回数据
        result = {
            "code": code,
            "dates": df['trade_date'].tolist(),
            "golden_crosses": [df['trade_date'].iloc[i] for i in golden_crosses],
            "death_crosses": [df['trade_date'].iloc[i] for i in death_crosses],
            "bullish_arrangements": [df['trade_date'].iloc[i] for i in bullish_arrangements],
            "macd_signals": {
                "golden_cross": [df['trade_date'].iloc[i] for i in macd_signals['golden_cross']],
                "death_cross": [df['trade_date'].iloc[i] for i in macd_signals['death_cross']],
                "bullish_momentum": [df['trade_date'].iloc[i] for i in macd_signals['bullish_momentum']],
                "bearish_momentum": [df['trade_date'].iloc[i] for i in macd_signals['bearish_momentum']]
            },
            "latest_state": latest_state
        }
        
        logger.info(f"get_stock_patterns 请求处理成功")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"处理 get_stock_patterns 请求失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
