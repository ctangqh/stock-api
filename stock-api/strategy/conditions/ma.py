"""
均线条件模块
实现基于移动平均线的选股条件
"""
from typing import Dict, Any, Optional
from datetime import date
import logging

from .base import Condition
from .operator import Operator, compare_values

logger = logging.getLogger(__name__)


class MACondition(Condition):
    """
    均线条件类
    
    用于判断股价与指定周期均线的关系
    """
    
    def __init__(self, ma_period: int, operator: Operator, reference_value: Optional[float] = None):
        """
        初始化均线条件
        
        :param ma_period: 均线周期 (5, 10, 20, 60等)
        :param operator: 比较操作符
        :param reference_value: 参考值，如果为None则比较当前股价与均线
        """
        self.ma_period = ma_period
        self.operator = operator
        self.reference_value = reference_value
    
    def evaluate(self, stock_code: str, stock_data: Dict[str, Any], 
                 scan_date: date, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        评估股票是否满足均线条件
        """
        try:
            ma_key = f'ma{self.ma_period}'
            
            # 获取最新技术指标
            latest_indicator = None
            if context and 'stock_latest_indicator' in context:
                latest_indicator = context['stock_latest_indicator'].get(stock_code)
            
            if not latest_indicator:
                logger.warning(f"未找到 {stock_code} 的技术指标数据")
                return False
            
            ma_value = latest_indicator.get(ma_key)
            if ma_value is None:
                logger.warning(f"未找到 {stock_code} 的 {ma_key} 数据")
                return False
            
            # 确定比较值
            if self.reference_value is not None:
                compare_value = self.reference_value
            else:
                compare_value = stock_data.get('close')
                if compare_value is None:
                    logger.warning(f"未找到 {stock_code} 的收盘价数据")
                    return False
            
            # 执行比较
            return compare_values(ma_value, self.operator, compare_value)
            
        except Exception as e:
            logger.error(f"评估 {stock_code} 的均线条件失败: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': 'ma',
            'ma_period': self.ma_period,
            'operator': self.operator.value,
            'reference_value': self.reference_value
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'MACondition':
        """从字典创建实例"""
        return cls(
            ma_period=config['ma_period'],
            operator=Operator(config['operator']),
            reference_value=config.get('reference_value')
        )
