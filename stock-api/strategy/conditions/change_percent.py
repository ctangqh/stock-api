"""
涨跌幅条件模块
实现基于涨跌幅的选股条件
"""
from typing import Dict, Any, Optional
from datetime import date
import logging

from .base import Condition
from .operator import Operator, compare_values

logger = logging.getLogger(__name__)


class ChangePercentCondition(Condition):
    """
    涨跌幅条件类
    
    用于判断股票涨跌幅是否满足指定条件
    """
    
    def __init__(self, operator: Operator, target_value: float):
        """
        初始化涨跌幅条件
        
        :param operator: 比较操作符
        :param target_value: 目标涨跌幅值（%）
        """
        self.operator = operator
        self.target_value = target_value
    
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
            
            return compare_values(change_percent, self.operator, self.target_value)
            
        except Exception as e:
            logger.error(f"评估 {stock_code} 的涨跌幅条件失败: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': 'change_percent',
            'operator': self.operator.value,
            'target_value': self.target_value
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ChangePercentCondition':
        """从字典创建实例"""
        return cls(
            operator=Operator(config['operator']),
            target_value=config['target_value']
        )
