"""
策略执行器模块
负责执行选股策略并返回结果
"""
from typing import List, Dict, Any, Optional
from datetime import date
import logging

from .conditions import Condition
from .parser import StrategyParser
from util.StockUtil import fetch_stock_indicators
from data.stock_cn_history_market import StockCnHistoryMarketORM
from conf.Config import DB_CONFIG

logger = logging.getLogger(__name__)


class StockSelector:
    """
    股票选择器类
    
    负责执行选股策略，筛选符合条件的股票
    """
    
    def __init__(self, strategy_config: Dict[str, Any]):
        """
        初始化股票选择器
        
        :param strategy_config: 策略配置字典
        """
        self.strategy_config = strategy_config
        self.condition = StrategyParser.parse_strategy(strategy_config)
        self._market_orm = StockCnHistoryMarketORM(DB_CONFIG)
    
    def select(self, scan_date: date, stock_list: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        执行选股策略
        
        :param scan_date: 选股日期
        :param stock_list: 可选的股票列表，如果为None则从数据库获取当天所有股票
        :return: 符合条件的股票列表
        """
        logger.info(f"开始执行选股策略，日期: {scan_date}")
        
        # 获取股票数据
        if stock_list is None:
            stock_list = self._market_orm.get_by_data_date(scan_date)
            logger.info(f"从数据库获取到 {len(stock_list)} 只股票")
        
        if not stock_list:
            logger.warning("没有可筛选的股票数据")
            return []
        
        # 批量获取技术指标
        stock_codes = [s['code'] for s in stock_list]
        stock_indicators, stock_latest_indicator = fetch_stock_indicators(
            stock_list, scan_date, days_back=60
        )
        
        # 构建上下文
        context = {
            'stock_indicators': stock_indicators,
            'stock_latest_indicator': stock_latest_indicator
        }
        
        # 筛选股票
        selected_stocks = []
        for stock_data in stock_list:
            stock_code = stock_data['code']
            try:
                if self.condition.evaluate(stock_code, stock_data, scan_date, context):
                    selected_stocks.append(stock_data)
            except Exception as e:
                logger.error(f"评估股票 {stock_code} 时出错: {e}")
                continue
        
        logger.info(f"选股完成，符合条件的股票: {len(selected_stocks)} 只")
        return selected_stocks
