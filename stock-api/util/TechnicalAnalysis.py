import pandas as pd
import numpy as np
import logging
from conf.Config import TECHNICAL_CONFIG

# 配置日志输出
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """
    计算简单移动平均线（SMA）
    
    :param prices: 价格序列
    :param period: 周期
    :return: SMA 序列
    """
    logger.debug(f"计算 SMA，周期: {period}")
    return prices.rolling(window=period).mean()


def calculate_ema(prices: pd.Series, period: int, adjust: bool = False) -> pd.Series:
    """
    计算指数移动平均线（EMA）
    
    :param prices: 价格序列
    :param period: 周期
    :param adjust: 是否使用调整因子，默认为 False（技术分析标准）
    :return: EMA 序列
    """
    logger.debug(f"计算 EMA，周期: {period}，adjust: {adjust}")
    return prices.ewm(span=period, adjust=adjust).mean()


def calculate_macd(
    prices: pd.Series,
    fast: int | None = None,
    slow: int | None = None,
    signal: int | None = None,
    adjust: bool = False
) -> dict[str, pd.Series]:
    """
    计算 MACD 指标
    
    :param prices: 价格序列
    :param fast: 快线周期，默认从配置读取
    :param slow: 慢线周期，默认从配置读取
    :param signal: 信号线周期，默认从配置读取
    :param adjust: 是否使用调整因子计算 EMA，默认为 False
    :return: 包含 DIF、DEA 和 MACD 柱状图的字典
    """
    if fast is None:
        fast = int(TECHNICAL_CONFIG['MACD_FAST'])
    if slow is None:
        slow = int(TECHNICAL_CONFIG['MACD_SLOW'])
    if signal is None:
        signal = int(TECHNICAL_CONFIG['MACD_SIGNAL'])
    
    logger.debug(f"计算 MACD，fast: {fast}, slow: {slow}, signal: {signal}")
    
    ema_fast = calculate_ema(prices, fast, adjust=adjust)
    ema_slow = calculate_ema(prices, slow, adjust=adjust)
    dif = ema_fast - ema_slow
    dea = calculate_ema(dif, signal, adjust=adjust)
    macd_hist = (dif - dea) * 2
    
    return {
        'dif': dif,
        'dea': dea,
        'macd_hist': macd_hist
    }


def detect_golden_cross(short_ma: pd.Series, long_ma: pd.Series) -> list[int]:
    """
    检测金叉（短期均线上穿长期均线）
    
    :param short_ma: 短期均线
    :param long_ma: 长期均线
    :return: 金叉位置索引列表
    """
    golden_crosses = []
    for i in range(1, len(short_ma)):
        if (not pd.isna(short_ma.iloc[i-1]) and not pd.isna(long_ma.iloc[i-1]) and
            not pd.isna(short_ma.iloc[i]) and not pd.isna(long_ma.iloc[i])):
            if short_ma.iloc[i-1] < long_ma.iloc[i-1] and short_ma.iloc[i] > long_ma.iloc[i]:
                golden_crosses.append(i)
    return golden_crosses


def detect_death_cross(short_ma: pd.Series, long_ma: pd.Series) -> list[int]:
    """
    检测死叉（短期均线下穿长期均线）
    
    :param short_ma: 短期均线
    :param long_ma: 长期均线
    :return: 死叉位置索引列表
    """
    death_crosses = []
    for i in range(1, len(short_ma)):
        if (not pd.isna(short_ma.iloc[i-1]) and not pd.isna(long_ma.iloc[i-1]) and
            not pd.isna(short_ma.iloc[i]) and not pd.isna(long_ma.iloc[i])):
            if short_ma.iloc[i-1] > long_ma.iloc[i-1] and short_ma.iloc[i] < long_ma.iloc[i]:
                death_crosses.append(i)
    return death_crosses


def detect_bullish_arrangement(
    ma5: pd.Series,
    ma10: pd.Series,
    ma20: pd.Series,
    ma60: pd.Series
) -> list[int]:
    """
    检测多头排列（MA5 > MA10 > MA20 > MA60）
    
    :param ma5: 5日均线
    :param ma10: 10日均线
    :param ma20: 20日均线
    :param ma60: 60日均线
    :return: 多头排列位置索引列表
    """
    bullish = []
    for i in range(len(ma5)):
        if (not pd.isna(ma5.iloc[i]) and not pd.isna(ma10.iloc[i]) and
            not pd.isna(ma20.iloc[i]) and not pd.isna(ma60.iloc[i])):
            if ma5.iloc[i] > ma10.iloc[i] > ma20.iloc[i] > ma60.iloc[i]:
                bullish.append(i)
    return bullish


def macd_signal_analysis(
    dif: pd.Series,
    dea: pd.Series,
    macd_hist: pd.Series
) -> dict[str, list[int]]:
    """
    分析 MACD 信号
    
    :param dif: DIF 线
    :param dea: DEA 线
    :param macd_hist: MACD 柱状图
    :return: 包含各种信号位置的字典
    """
    golden_cross = []
    death_cross = []
    bullish_momentum = []
    bearish_momentum = []
    
    for i in range(1, len(dif)):
        if (not pd.isna(dif.iloc[i-1]) and not pd.isna(dea.iloc[i-1]) and
            not pd.isna(dif.iloc[i]) and not pd.isna(dea.iloc[i])):
            # 金叉：DIF 上穿 DEA
            if dif.iloc[i-1] < dea.iloc[i-1] and dif.iloc[i] > dea.iloc[i]:
                golden_cross.append(i)
            # 死叉：DIF 下穿 DEA
            if dif.iloc[i-1] > dea.iloc[i-1] and dif.iloc[i] < dea.iloc[i]:
                death_cross.append(i)
        
        if (not pd.isna(macd_hist.iloc[i-1]) and not pd.isna(macd_hist.iloc[i])):
            # 红柱变长
            if macd_hist.iloc[i] > 0 and macd_hist.iloc[i] > macd_hist.iloc[i-1]:
                bullish_momentum.append(i)
            # 绿柱变长
            if macd_hist.iloc[i] < 0 and abs(macd_hist.iloc[i]) > abs(macd_hist.iloc[i-1]):
                bearish_momentum.append(i)
    
    return {
        'golden_cross': golden_cross,
        'death_cross': death_cross,
        'bullish_momentum': bullish_momentum,
        'bearish_momentum': bearish_momentum
    }


if __name__ == "__main__":
    # 简单测试
    logger.info("测试技术分析模块")
    
    # 创建测试数据
    np.random.seed(42)
    test_prices = pd.Series(np.random.randn(100).cumsum() + 100)
    logger.info(f"测试数据: {test_prices.head()}")
    
    # 测试 SMA
    sma5 = calculate_sma(test_prices, 5)
    logger.info(f"SMA5: {sma5.head()}")
    
    # 测试 EMA
    ema12 = calculate_ema(test_prices, 12)
    logger.info(f"EMA12: {ema12.head()}")
    
    # 测试 MACD
    macd = calculate_macd(test_prices)
    logger.info(f"MACD DIF: {macd['dif'].head()}")
    
    # 测试金叉死叉
    sma10 = calculate_sma(test_prices, 10)
    golden = detect_golden_cross(sma5, sma10)
    death = detect_death_cross(sma5, sma10)
    logger.info(f"金叉位置: {golden[:5]}")
    logger.info(f"死叉位置: {death[:5]}")
    
    logger.info("测试完成")
