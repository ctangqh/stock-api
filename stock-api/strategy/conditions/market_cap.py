"""
市值条件模块
实现基于市值的选股条件
"""
from typing import Dict, Any, Optional
from datetime import date
import logging

from .base import Condition
from .operator import Operator, compare_values

logger = logging.getLogger(__name__)


class MarketCapCondition(Condition):
    """
    市值条件类
    
    用于判断股票市值是否满足指定条件
    """
    
    def __init__(self, operator: Operator, target_value: float):
        """
        初始化市值条件
        
        :param operator: 比较操作符
        :param target_value: 目标市值（亿元）
        """
        self.operator = operator
        self.target_value = target_value
    
    def evaluate(self, stock_code: str, stock_data: Dict[str, Any], 
                 scan_date: date, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        评估股票是否满足市值条件
        """
        try:
            market_value = stock_data.get('market_value')
            
            if market_value is None:
                # 尝试从 context 中获取市值（如果 stock_data 中没有）
                if context and 'stock_market_caps' in context:
                    market_cap_100m = context['stock_market_caps'].get(stock_code)
                    if market_cap_100m is None:
                        logger.warning(f"未找到 {stock_code} 的市值数据")
                        return False
                else:
                    logger.warning(f"未找到 {stock_code} 的市值数据")
                    return False
            else:
                # 转换为亿元（数据库中通常是元）
                market_cap_100m = market_value / 100000000.0
            
            return compare_values(market_cap_100m, self.operator, self.target_value)
            
        except Exception as e:
            logger.error(f"评估 {stock_code} 的市值条件失败: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': 'market_cap',
            'operator': self.operator.value,
            'target_value': self.target_value
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'MarketCapCondition':
        """从字典创建实例"""
        return cls(
            operator=Operator(config['operator']),
            target_value=config['target_value']
        )
