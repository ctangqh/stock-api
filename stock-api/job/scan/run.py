from typing import List, Dict, Any, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

from .filter_change_percent import filter_change_percent
from .filter_market_cap import filter_market_cap
from .filter_ma import filter_ma, Operator as OldOperator
from .filter_up import filter_up

STRATEGY_CONDITIONS_AVAILABLE = False
try:
    from strategy.conditions import (
        Condition,
        ChangePercentCondition,
        MarketCapCondition,
        MACondition,
        AndCompositeCondition,
        OrCompositeCondition,
        Operator
    )
    from strategy.parser import StrategyParser
    STRATEGY_CONDITIONS_AVAILABLE = True
    logger.info("策略条件模块导入成功")
except ImportError as e:
    logger.warning(f"策略条件模块导入失败: {e}")
    STRATEGY_CONDITIONS_AVAILABLE = False


class FilterStrategy:
    def __init__(self, strategy_config: Dict[str, Any]):
        self._config = strategy_config
    
    def get_type(self) -> str:
        return self._config.get('type', '')
    
    def get_param(self, key: str, default: Any = None) -> Any:
        return self._config.get('params', {}).get(key, default)


class ScanJob:
    def __init__(self):
        self._filters = {}
        self._register_default_filters()
    
    def _register_default_filters(self):
        self.register_filter('change_percent', filter_change_percent)
        self.register_filter('market_cap', filter_market_cap)
        self.register_filter('ma', filter_ma)
        self.register_filter('continuous_up', filter_up)
    
    def register_filter(self, name: str, filter_func):
        self._filters[name] = filter_func
        logger.debug(f"注册过滤器: {name}")
    
    def get_registered_filters(self) -> List[str]:
        filters = set(self._filters.keys())
        if STRATEGY_CONDITIONS_AVAILABLE:
            filters.update(['and', 'or', 'change_percent', 'market_cap', 'ma', 'continuous_rise'])
        return sorted(list(filters))
    
    def run(
        self,
        strategy_config: Dict[str, Any],
        stocks: List[Dict[str, Any]],
        scan_date: date,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.debug(f"STRATEGY_CONDITIONS_AVAILABLE: {STRATEGY_CONDITIONS_AVAILABLE}")
        logger.debug(f"strategy_config: {strategy_config}")
        
        use_new_format = (
            STRATEGY_CONDITIONS_AVAILABLE 
            and 'type' in strategy_config 
            and strategy_config['type'] in ['and', 'or', 'change_percent', 'market_cap', 'ma', 'continuous_rise']
        )
        
        logger.debug(f"use_new_format: {use_new_format}")
        
        if use_new_format:
            return self._run_with_strategy_conditions(strategy_config, stocks, scan_date, **kwargs)
        else:
            return self._run_with_old_filters(strategy_config, stocks, scan_date, **kwargs)
    
    def _run_with_old_filters(
        self,
        strategy_config: Dict[str, Any],
        stocks: List[Dict[str, Any]],
        scan_date: date,
        **kwargs
    ) -> List[Dict[str, Any]]:
        filters = strategy_config.get('filters', [])
        logger.info(f"开始执行筛选任务（旧过滤器格式），共 {len(filters)} 个过滤器")
        
        current_stocks = stocks
        
        for i, filter_config in enumerate(filters, 1):
            filter_type = filter_config.get('type')
            
            if not filter_type:
                logger.warning(f"过滤器 {i} 缺少 'type' 字段，跳过")
                continue
            
            if filter_type not in self._filters:
                logger.warning(f"未知的过滤器类型: {filter_type}，跳过")
                continue
            
            filter_func = self._filters[filter_type]
            logger.info(f"执行过滤器 {i}/{len(filters)}: {filter_type}")
            logger.info(f"  过滤器参数: {filter_config.get('params', {})}")
            
            current_stocks = self._apply_filter(
                filter_func,
                filter_config,
                current_stocks,
                scan_date,
                **kwargs
            )
            
            if not current_stocks:
                logger.info(f"过滤器 {filter_type} 后无股票，提前结束")
                break
        
        logger.info(f"筛选任务完成，最终结果: {len(current_stocks)} 只股票")
        return current_stocks
    
    def _run_with_strategy_conditions(
        self,
        strategy_config: Dict[str, Any],
        stocks: List[Dict[str, Any]],
        scan_date: date,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.info(f"开始执行筛选任务（新策略条件格式）")
        
        condition = StrategyParser.parse_strategy(strategy_config)
        
        context = {
            'stock_market_caps': kwargs.get('stock_market_caps', {}),
            'stock_latest_indicator': kwargs.get('stock_latest_indicator', {})
        }
        if 'stock_indicators' in kwargs:
            context['stock_indicators'] = kwargs['stock_indicators']
        
        selected_stocks = []
        for stock_data in stocks:
            stock_code = stock_data['code']
            try:
                if condition.evaluate(stock_code, stock_data, scan_date, context):
                    selected_stocks.append(stock_data)
            except Exception as e:
                logger.error(f"评估股票 {stock_code} 时出错: {e}")
                continue
        
        logger.info(f"筛选任务完成，最终结果: {len(selected_stocks)} 只股票")
        return selected_stocks
    
    def _apply_filter(
        self,
        filter_func,
        filter_config: Dict[str, Any],
        stocks: List[Dict[str, Any]],
        scan_date: date,
        **kwargs
    ) -> List[Dict[str, Any]]:
        filter_type = filter_config.get('type')
        params = filter_config.get('params', {})
        
        if filter_type == 'change_percent':
            return filter_func(
                stocks,
                min_change=params.get('min_change', 3.0),
                max_change=params.get('max_change', 6.0)
            )
        
        elif filter_type == 'market_cap':
            stock_market_caps = kwargs.get('stock_market_caps', {})
            return filter_func(
                stocks,
                stock_market_caps,
                min_cap=params.get('min_cap', 60.0),
                max_cap=params.get('max_cap', 800.0)
            )
        
        elif filter_type == 'ma':
            stock_latest_indicator = kwargs.get('stock_latest_indicator', {})
            operator_str = params.get('operator', '>=')
            operator = OldOperator(operator_str) if operator_str else OldOperator.GREATER_OR_EQUAL
            return filter_func(
                stocks,
                stock_latest_indicator,
                ma_period=params.get('ma_period', 20),
                operator=operator
            )
        
        elif filter_type == 'continuous_up':
            return filter_func(
                stocks,
                consecutive_days=params.get('days', 3),
                scan_date=scan_date
            )
        
        else:
            logger.warning(f"未处理的过滤器类型: {filter_type}")
            return stocks


_scan_job_instance = None


def get_scan_job() -> ScanJob:
    global _scan_job_instance
    if _scan_job_instance is None:
        _scan_job_instance = ScanJob()
    return _scan_job_instance


def run_scan_job(
    strategy_config: Dict[str, Any],
    stocks: List[Dict[str, Any]],
    scan_date: date,
    **kwargs
) -> List[Dict[str, Any]]:
    job = get_scan_job()
    return job.run(strategy_config, stocks, scan_date, **kwargs)


"""
策略配置 JSON 格式定义:

{
  "filters": [
    {
      "type": "change_percent",
      "params": {
        "min_change": 3.0,
        "max_change": 6.0
      }
    },
    {
      "type": "market_cap",
      "params": {
        "min_cap": 60.0,
        "max_cap": 800.0
      }
    },
    {
      "type": "ma",
      "params": {
        "ma_period": 20,
        "operator": ">="
      }
    },
    {
      "type": "continuous_up",
      "params": {
        "days": 3
      }
    }
  ]
}

过滤器类型说明:
- change_percent: 涨跌幅范围筛选
  - params.min_change: 最小涨跌幅(%)，默认 3.0
  - params.max_change: 最大涨跌幅(%)，默认 6.0

- market_cap: 市值范围筛选
  - params.min_cap: 最小市值(亿元)，默认 60.0
  - params.max_cap: 最大市值(亿元)，默认 800.0

- ma: 均线条件筛选
  - params.ma_period: 均线周期(5, 10, 20, 60)，默认 20
  - params.operator: 比较操作符(">", ">=", "<", "<=", "==")，默认 ">="
    - ">": 收盘价 > 均线
    - ">=": 收盘价 >= 均线
    - "<": 收盘价 < 均线
    - "<=": 收盘价 <= 均线
    - "==": 收盘价 == 均线

- continuous_up: 连续上涨筛选
  - params.days: 连续上涨天数，默认 3
"""
