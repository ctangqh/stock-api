"""
策略解析器模块
负责从 JSON 配置解析策略条件
"""
from typing import Dict, Any
import logging

from .conditions import (
    Condition,
    MACondition,
    MarketCapCondition,
    ChangePercentCondition,
    ContinuousRiseCondition,
    AndCompositeCondition,
    OrCompositeCondition
)

logger = logging.getLogger(__name__)


class StrategyParser:
    """
    策略解析器类
    
    负责从 JSON 配置解析出完整的条件树
    """
    
    # 条件类型映射
    _condition_types = {
        'ma': MACondition,
        'market_cap': MarketCapCondition,
        'change_percent': ChangePercentCondition,
        'continuous_rise': ContinuousRiseCondition,
        'and': AndCompositeCondition,
        'or': OrCompositeCondition
    }
    
    @classmethod
    def parse_condition(cls, config: Dict[str, Any]) -> Condition:
        """
        解析单个条件配置
        
        :param config: 条件配置字典
        :return: 条件实例
        """
        condition_type = config.get('type')
        if not condition_type:
            raise ValueError(f"条件配置缺少 'type' 字段: {config}")
        
        condition_class = cls._condition_types.get(condition_type)
        if not condition_class:
            raise ValueError(f"不支持的条件类型: {condition_type}")
        
        return condition_class.from_dict(config)
    
    @classmethod
    def parse_strategy(cls, strategy_config: Dict[str, Any]) -> Condition:
        """
        解析完整策略配置
        
        :param strategy_config: 策略配置字典
        :return: 根条件实例
        """
        logger.info(f"解析策略配置: {strategy_config}")
        return cls.parse_condition(strategy_config)
