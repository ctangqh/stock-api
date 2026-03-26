"""
条件基类模块
定义所有策略条件的抽象基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


class Condition(ABC):
    """
    所有策略条件的抽象基类
    
    每个具体条件都需要继承此类并实现 evaluate 方法
    """
    
    @abstractmethod
    def evaluate(self, stock_code: str, stock_data: Dict[str, Any], 
                 scan_date: date, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        评估股票是否满足此条件
        
        :param stock_code: 股票代码
        :param stock_data: 股票数据字典
        :param scan_date: 选股日期
        :param context: 上下文数据，用于在条件间共享数据
        :return: 是否满足条件
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        将条件转换为字典格式，用于序列化
        
        :return: 条件配置字典
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'Condition':
        """
        从字典创建条件实例
        
        :param config: 条件配置字典
        :return: 条件实例
        """
        pass
