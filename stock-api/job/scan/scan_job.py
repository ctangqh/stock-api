from typing import List, Dict, Any, Optional
from datetime import date
import logging

from .filter_change_percent import filter_change_percent
from .filter_market_cap import filter_market_cap
from .filter_ma import filter_ma, Operator
from .filter_up import filter_up

logger = logging.getLogger(__name__)


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
        return list(self._filters.keys())
    
    def run(
        self,
        filters: List[Dict[str, Any]],
        stocks: List[Dict[str, Any]],
        scan_date: date,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.info(f"开始执行筛选任务，共 {len(filters)} 个过滤器")
        
        current_stocks = stocks
        
        for i, filter_config in enumerate(filters, 1):
            filter_name = filter_config.get('type')
            
            if not filter_name:
                logger.warning(f"过滤器 {i} 缺少 'type' 字段，跳过")
                continue
            
            if filter_name not in self._filters:
                logger.warning(f"未知的过滤器类型: {filter_name}，跳过")
                continue
            
            filter_func = self._filters[filter_name]
            logger.info(f"执行过滤器 {i}/{len(filters)}: {filter_name}")
            
            current_stocks = self._apply_filter(
                filter_func,
                filter_config,
                current_stocks,
                scan_date,
                **kwargs
            )
            
            if not current_stocks:
                logger.info(f"过滤器 {filter_name} 后无股票，提前结束")
                break
        
        logger.info(f"筛选任务完成，最终结果: {len(current_stocks)} 只股票")
        return current_stocks
    
    def _apply_filter(
        self,
        filter_func,
        filter_config: Dict[str, Any],
        stocks: List[Dict[str, Any]],
        scan_date: date,
        **kwargs
    ) -> List[Dict[str, Any]]:
        filter_name = filter_config.get('type')
        
        if filter_name == 'change_percent':
            return filter_func(
                stocks,
                min_change=filter_config.get('min_change', 3.0),
                max_change=filter_config.get('max_change', 6.0)
            )
        
        elif filter_name == 'market_cap':
            stock_market_caps = kwargs.get('stock_market_caps', {})
            return filter_func(
                stocks,
                stock_market_caps,
                min_cap=filter_config.get('min_cap', 60.0),
                max_cap=filter_config.get('max_cap', 800.0)
            )
        
        elif filter_name == 'ma':
            stock_latest_indicator = kwargs.get('stock_latest_indicator', {})
            operator_str = filter_config.get('operator', '>=')
            operator = Operator(operator_str) if operator_str else Operator.GREATER_OR_EQUAL
            return filter_func(
                stocks,
                stock_latest_indicator,
                ma_period=filter_config.get('ma_period', 20),
                operator=operator
            )
        
        elif filter_name == 'continuous_up':
            return filter_func(
                stocks,
                consecutive_days=filter_config.get('days', 3),
                scan_date=scan_date
            )
        
        else:
            logger.warning(f"未处理的过滤器类型: {filter_name}")
            return stocks


_scan_job_instance = None


def get_scan_job() -> ScanJob:
    global _scan_job_instance
    if _scan_job_instance is None:
        _scan_job_instance = ScanJob()
    return _scan_job_instance


def run_scan_job(
    filters: List[Dict[str, Any]],
    stocks: List[Dict[str, Any]],
    scan_date: date,
    **kwargs
) -> List[Dict[str, Any]]:
    job = get_scan_job()
    return job.run(filters, stocks, scan_date, **kwargs)
