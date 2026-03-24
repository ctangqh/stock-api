import logging
import datetime
import pandas as pd
from typing import Optional, Dict, List

from conf.Config import TECHNICAL_CONFIG, DB_CONFIG, REDIS_CONFIG
from data.stock_cn_history_market import StockCnHistoryMarketORM
from util.RedisUtil import RedisUtil

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockHistoryDataFetcher:
    """
    股票历史行情数据获取类
    功能：从数据库 stock_cn_history_market 表读取数据，缓存到 Redis
    """

    def __init__(self, db_config: Dict, redis_config: Dict):
        """
        初始化数据获取类
        
        参数:
        db_config -- 数据库配置字典
        redis_config -- Redis 配置字典
        """
        logger.info("初始化 StockHistoryDataFetcher")
        self.orm = StockCnHistoryMarketORM(db_config)
        self.redis = RedisUtil(redis_config)

    def _generate_cache_key(self, symbol: str, start_date: str, end_date: str) -> str:
        """
        生成 Redis 缓存键
        
        参数:
        symbol -- 股票代码
        start_date -- 开始日期
        end_date -- 结束日期
        
        返回:
        str -- 缓存键
        """
        return f"stock_history_{symbol}_{start_date}_{end_date}"

    def fetch_stock_history(self, symbol: str, days: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        获取股票历史行情数据
        
        参数:
        symbol -- 股票代码
        days -- 获取天数，默认使用 TECHNICAL_CONFIG 中的配置
        
        返回:
        pd.DataFrame -- 历史行情数据，失败返回 None
        """
        if days is None:
            days = TECHNICAL_CONFIG['DEFAULT_LOOKBACK_DAYS']
        
        end_date = datetime.date.today().strftime('%Y%m%d')
        start_date = (datetime.date.today() - datetime.timedelta(days=days)).strftime('%Y%m%d')
        
        cache_key = self._generate_cache_key(symbol, start_date, end_date)
        
        # 检查 Redis 缓存
        cached_data = self.redis.get(cache_key)
        if cached_data is not None:
            logger.info(f"从 Redis 缓存获取数据: {cache_key}")
            return pd.DataFrame(cached_data)
        
        # 缓存不存在，从数据库获取
        try:
            logger.info(f"从数据库获取股票历史行情: {symbol}")
            data_list = self.orm.get_latest_by_code(symbol, days)
            
            if not data_list:
                logger.warning(f"数据库中未找到股票 {symbol} 的历史行情数据")
                return None
            
            df = pd.DataFrame(data_list)
            
            # 缓存数据到 Redis，24小时过期
            self.redis.set(cache_key, df.to_dict('records'), ex=86400)
            logger.info(f"数据已缓存到 Redis: {cache_key}")
            
            return df
        except Exception as e:
            logger.error(f"获取股票历史行情失败: {symbol}, 错误: {e}")
            return None

    def sync_to_database(self, df: pd.DataFrame, ts_code: Optional[str] = None) -> int:
        """
        将 DataFrame 同步到数据库（保留方法兼容性，实际不再需要从 akshare 同步）
        
        参数:
        df -- 历史行情 DataFrame
        ts_code -- 股票代码，可选
        
        返回:
        int -- 成功插入的记录数，当前始终返回 0
        """
        logger.warning("sync_to_database 方法已废弃，数据现在直接从数据库读取")
        return 0


if __name__ == "__main__":
    # 简单测试
    logger.info("测试 StockHistoryDataFetcher 模块")
    fetcher = StockHistoryDataFetcher(DB_CONFIG, REDIS_CONFIG)
    logger.info("StockHistoryDataFetcher 初始化成功")
