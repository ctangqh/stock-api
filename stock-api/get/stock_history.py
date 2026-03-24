import logging
import datetime
import pandas as pd
from typing import Optional, Dict, List

from conf.Config import TECHNICAL_CONFIG, DB_CONFIG
from data.stock_cn_history_market import StockCnHistoryMarketORM

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockHistoryDataFetcher:
    """
    股票历史行情数据获取类
    功能：从数据库 stock_cn_history_market 表读取数据
    """

    def __init__(self, db_config: Dict):
        """
        初始化数据获取类
        
        参数:
        db_config -- 数据库配置字典
        """
        logger.info("初始化 StockHistoryDataFetcher")
        self.orm = StockCnHistoryMarketORM(db_config)

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
        
        # 从数据库获取
        try:
            logger.info(f"从数据库获取股票历史行情: {symbol}")
            data_list = self.orm.get_latest_by_code(symbol, days)
            
            if not data_list:
                logger.warning(f"数据库中未找到股票 {symbol} 的历史行情数据")
                return None
            
            df = pd.DataFrame(data_list)
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
    fetcher = StockHistoryDataFetcher(DB_CONFIG)
    logger.info("StockHistoryDataFetcher 初始化成功")
