"""
组合条件模块
实现逻辑组合条件（AND、OR）
"""
from typing import Dict, Any, Optional, List
from datetime import date
import logging

from .base import Condition

logger = logging.getLogger(__name__)


class AndCompositeCondition(Condition):
    """
    AND 组合条件类
    
    所有子条件都满足时才返回 True
    """
    
    def __init__(self, conditions: List[Condition]):
        """
        初始化 AND 组合条件
        
        :param conditions: 子条件列表
        """
        self.conditions = conditions
    
    def evaluate(self, stock_code: str, stock_data: Dict[str, Any], 
                 scan_date: date, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        评估股票是否满足所有子条件
        """
        for condition in self.conditions:
            if not condition.evaluate(stock_code, stock_data, scan_date, context):
                return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': 'and',
            'conditions': [cond.to_dict() for cond in self.conditions]
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'AndCompositeCondition':
        """从字典创建实例（需要依赖解析器）"""
        from ..parser import StrategyParser
        conditions = [StrategyParser.parse_condition(cond) for cond in config['conditions']]
        return cls(conditions=conditions)


class OrCompositeCondition(Condition):
    """
    OR 组合条件类
    
    至少有一个子条件满足时就返回 True
    """
    
    def __init__(self, conditions: List[Condition]):
        """
        初始化 OR 组合条件
        
        :param conditions: 子条件列表
        """
        self.conditions = conditions
    
    def evaluate(self, stock_code: str, stock_data: Dict[str, Any], 
                 scan_date: date, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        评估股票是否满足至少一个子条件
        """
        for condition in self.conditions:
            if condition.evaluate(stock_code, stock_data, scan_date, context):
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': 'or',
            'conditions': [cond.to_dict() for cond in self.conditions]
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'OrCompositeCondition':
        """从字典创建实例（需要依赖解析器）"""
        from ..parser import StrategyParser
        conditions = [StrategyParser.parse_condition(cond) for cond in config['conditions']]
        return cls(conditions=conditions)
