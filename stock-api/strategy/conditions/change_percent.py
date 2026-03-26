"""
涨跌幅条件模块
实现基于涨跌幅的选股条件
"""
from typing import Dict, Any, Optional
from datetime import date
import logging

from .base import Condition

logger = logging.getLogger(__name__)


class ChangePercentCondition(Condition):
    """
    涨跌幅条件类
    
    用于判断股票涨跌幅是否在指定范围内
    """
    
    def __init__(self, min_change: Optional[float] = None, max_change: Optional[float] = None):
        """
        初始化涨跌幅条件
        
        :param min_change: 最小涨跌幅（%），为None表示不限制
        :param max_change: 最大涨跌幅（%），为None表示不限制
        """
        self.min_change = min_change
        self.max_change = max_change
    
    def evaluate(self, stock_code: str, stock_data: Dict[str, Any], 
                 scan_date: date, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        评估股票是否满足涨跌幅条件
        """
        try:
            change_percent = stock_data.get('change_percent')
            
            if change_percent is None:
                logger.warning(f"未找到 {stock_code} 的涨跌幅数据")
                return False
            
            # 检查下限
            if self.min_change is not None and change_percent < self.min_change:
                return False
            
            # 检查上限
            if self.max_change is not None and change_percent > self.max_change:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"评估 {stock_code} 的涨跌幅条件失败: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': 'change_percent',
            'min_change': self.min_change,
            'max_change': self.max_change
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ChangePercentCondition':
        """从字典创建实例"""
        return cls(
            min_change=config.get('min_change'),
            max_change=config.get('max_change')
        )
