"""
连续上涨条件模块
实现基于连续上涨天数的选股条件
"""
from typing import Dict, Any, Optional, List
from datetime import date
import pandas as pd
import logging

from .base import Condition
from data.stock_cn_history_market import StockCnHistoryMarketORM
from conf.Config import DB_CONFIG

logger = logging.getLogger(__name__)


class ContinuousRiseCondition(Condition):
    """
    连续上涨条件类
    
    用于判断股票是否连续指定天数上涨
    """
    
    def __init__(self, days: int = 3):
        """
        初始化连续上涨条件
        
        :param days: 连续上涨天数
        """
        self.days = days
        self._market_orm = StockCnHistoryMarketORM(DB_CONFIG)
    
    def evaluate(self, stock_code: str, stock_data: Dict[str, Any], 
                 scan_date: date, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        评估股票是否满足连续上涨条件
        """
        try:
            # 获取最近N+1天的数据
            recent_data = self._market_orm.get_by_code(stock_code, limit=self.days + 1)
            
            if len(recent_data) < self.days:
                logger.warning(f"{stock_code} 的历史数据不足 {self.days} 天")
                return False
            
            # 转换为DataFrame并排序
            df = pd.DataFrame(recent_data)
            df = df.sort_values('data_date').tail(self.days).reset_index(drop=True)
            
            # 检查每天是否都上涨
            all_rise = True
            for i in range(len(df)):
                change_percent = df.iloc[i].get('change_percent')
                if change_percent is None or change_percent <= 0:
                    all_rise = False
                    break
            
            return all_rise
            
        except Exception as e:
            logger.error(f"评估 {stock_code} 的连续上涨条件失败: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': 'continuous_rise',
            'days': self.days
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ContinuousRiseCondition':
        """从字典创建实例"""
        return cls(
            days=config.get('days', 3)
        )
