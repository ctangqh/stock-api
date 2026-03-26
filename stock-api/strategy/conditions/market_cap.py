"""
市值条件模块
实现基于市值的选股条件
"""
from typing import Dict, Any, Optional
from datetime import date
import logging

from .base import Condition

logger = logging.getLogger(__name__)


class MarketCapCondition(Condition):
    """
    市值条件类
    
    用于判断股票市值是否在指定范围内
    """
    
    def __init__(self, min_cap: Optional[float] = None, max_cap: Optional[float] = None):
        """
        初始化市值条件
        
        :param min_cap: 最小市值（亿元），为None表示不限制
        :param max_cap: 最大市值（亿元），为None表示不限制
        """
        self.min_cap = min_cap
        self.max_cap = max_cap
    
    def evaluate(self, stock_code: str, stock_data: Dict[str, Any], 
                 scan_date: date, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        评估股票是否满足市值条件
        """
        try:
            market_value = stock_data.get('market_value')
            
            if market_value is None:
                logger.warning(f"未找到 {stock_code} 的市值数据")
                return False
            
            # 转换为亿元（数据库中通常是元）
            # 根据实际数据结构调整，这里假设market_value是元为单位
            market_cap_100m = market_value / 100000000.0
            
            # 检查下限
            if self.min_cap is not None and market_cap_100m < self.min_cap:
                return False
            
            # 检查上限
            if self.max_cap is not None and market_cap_100m > self.max_cap:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"评估 {stock_code} 的市值条件失败: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': 'market_cap',
            'min_cap': self.min_cap,
            'max_cap': self.max_cap
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'MarketCapCondition':
        """从字典创建实例"""
        return cls(
            min_cap=config.get('min_cap'),
            max_cap=config.get('max_cap')
        )
