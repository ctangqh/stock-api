import pytest
import pandas as pd
import numpy as np
from util.TechnicalAnalysis import (
    calculate_sma,
    calculate_ema,
    calculate_macd,
    detect_golden_cross,
    detect_death_cross,
    detect_bullish_arrangement,
    macd_signal_analysis
)


@pytest.mark.unit
def test_sma_calculation():
    """测试简单移动平均线（SMA）计算"""
    prices = pd.Series([10, 11, 12, 13, 14, 15])
    sma = calculate_sma(prices, 3)
    
    # 验证前 period-1 个值为 NaN
    assert pd.isna(sma.iloc[0])
    assert pd.isna(sma.iloc[1])
    
    # 验证计算结果
    assert sma.iloc[2] == pytest.approx(11.0)  # (10+11+12)/3
    assert sma.iloc[3] == pytest.approx(12.0)  # (11+12+13)/3
    assert sma.iloc[4] == pytest.approx(13.0)  # (12+13+14)/3


@pytest.mark.unit
def test_ema_calculation():
    """测试指数移动平均线（EMA）计算"""
    prices = pd.Series([10, 11, 12, 13, 14, 15])
    ema = calculate_ema(prices, 3, adjust=False)
    
    # 手动计算验证
    alpha = 2 / (3 + 1)  # 0.5
    expected_ema = pd.Series([
        10.0,
        10 + alpha * (11 - 10),
        10.5 + alpha * (12 - 10.5),
        11.25 + alpha * (13 - 11.25),
        12.125 + alpha * (14 - 12.125),
        13.0625 + alpha * (15 - 13.0625)
    ])
    
    # 验证计算结果
    pd.testing.assert_series_equal(ema, expected_ema, check_names=False)


@pytest.mark.unit
def test_macd_calculation():
    """测试 MACD 指标计算"""
    prices = pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    macd = calculate_macd(prices, fast=3, slow=5, signal=2)
    
    # 验证返回字典包含必要的键
    assert 'dif' in macd
    assert 'dea' in macd
    assert 'macd_hist' in macd
    
    # 验证长度一致
    assert len(macd['dif']) == len(prices)
    assert len(macd['dea']) == len(prices)
    assert len(macd['macd_hist']) == len(prices)
    
    # 验证公式：MACD柱 = (DIF - DEA) * 2
    for i in range(len(prices)):
        if not pd.isna(macd['dif'].iloc[i]) and not pd.isna(macd['dea'].iloc[i]):
            assert macd['macd_hist'].iloc[i] == pytest.approx((macd['dif'].iloc[i] - macd['dea'].iloc[i]) * 2)


@pytest.mark.unit
def test_golden_cross_detection():
    """测试金叉检测"""
    short_ma = pd.Series([9, 10, 11, 10])
    long_ma = pd.Series([10, 10, 10, 12])
    
    golden_crosses = detect_golden_cross(short_ma, long_ma)
    
    # 验证在索引 2 检测到金叉
    assert 2 in golden_crosses
    # 验证其他位置不是金叉
    assert 1 not in golden_crosses
    assert 3 not in golden_crosses


@pytest.mark.unit
def test_death_cross_detection():
    """测试死叉检测"""
    short_ma = pd.Series([11, 10, 9, 10])
    long_ma = pd.Series([10, 10, 10, 8])
    
    death_crosses = detect_death_cross(short_ma, long_ma)
    
    # 验证在索引 2 检测到死叉
    assert 2 in death_crosses
    # 验证其他位置不是死叉
    assert 1 not in death_crosses
    assert 3 not in death_crosses


@pytest.mark.unit
def test_bullish_arrangement():
    """测试多头排列检测"""
    ma5 = pd.Series([20, 21, 22, 20])
    ma10 = pd.Series([19, 20, 21, 21])
    ma20 = pd.Series([18, 19, 20, 19])
    ma60 = pd.Series([17, 18, 19, 22])
    
    bullish = detect_bullish_arrangement(ma5, ma10, ma20, ma60)
    
    # 验证在索引 0, 1, 2 检测到多头排列
    assert 0 in bullish
    assert 1 in bullish
    assert 2 in bullish
    # 验证索引 3 不是多头排列
    assert 3 not in bullish


@pytest.mark.unit
def test_macd_signal_analysis():
    """测试 MACD 信号分析"""
    # 创建测试数据
    dif = pd.Series([1, 2, 3, 4, 3, 2, 1])
    dea = pd.Series([2, 2, 2, 3, 4, 4, 4])
    macd_hist = pd.Series([-2, 0, 2, 2, -2, -4, -6])
    
    signals = macd_signal_analysis(dif, dea, macd_hist)
    
    # 验证金叉
    assert 2 in signals['golden_cross']
    # 验证死叉
    assert 4 in signals['death_cross']
    # 验证红柱变长
    assert 3 in signals['bullish_momentum']
    # 验证绿柱变长
    assert 5 in signals['bearish_momentum']
    assert 6 in signals['bearish_momentum']


@pytest.mark.unit
def test_edge_cases():
    """测试边界情况"""
    # 测试数据不足
    short_prices = pd.Series([10, 11])
    
    # SMA 测试
    sma = calculate_sma(short_prices, 3)
    assert pd.isna(sma.iloc[0])
    assert pd.isna(sma.iloc[1])
    
    # EMA 测试
    ema = calculate_ema(short_prices, 3)
    assert not pd.isna(ema.iloc[0])
    assert not pd.isna(ema.iloc[1])
    
    # 包含 NaN 的情况
    nan_prices = pd.Series([10, np.nan, 12, 13, np.nan, 15])
    sma_nan = calculate_sma(nan_prices, 3)
    # 验证计算跳过 NaN 但结果正确
    assert pd.isna(sma_nan.iloc[0])
    assert pd.isna(sma_nan.iloc[1])
    assert pd.isna(sma_nan.iloc[2])  # 因为有 NaN
    assert not pd.isna(sma_nan.iloc[3])  # 11,12,13 的平均


if __name__ == "__main__":
    pytest.main([__file__])
