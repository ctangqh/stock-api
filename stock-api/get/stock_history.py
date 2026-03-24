import logging
import datetime
import time
import akshare as ak
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
    功能：从 akshare 获取数据，缓存到 Redis，同步到数据库
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
        
        # 缓存不存在，从 akshare 获取
        try:
            logger.info(f"从 akshare 获取股票历史行情: {symbol}")
            time.sleep(0.1)  # 避免触发反爬虫
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            
            # 缓存数据到 Redis，24小时过期
            self.redis.set(cache_key, df.to_dict('records'), ex=86400)
            logger.info(f"数据已缓存到 Redis: {cache_key}")
            
            return df
        except Exception as e:
            logger.error(f"获取股票历史行情失败: {symbol}, 错误: {e}")
            return None

    def sync_to_database(self, df: pd.DataFrame, ts_code: Optional[str] = None) -> int:
        """
        将 DataFrame 同步到数据库
        
        参数:
        df -- 历史行情 DataFrame
        ts_code -- 股票代码，可选（从 df 提取或传入）
        
        返回:
        int -- 成功插入的记录数
        """
        if df.empty:
            logger.warning("DataFrame 为空，跳过同步")
            return 0
        
        # 准备数据列表
        data_list = df.to_dict('records')
        
        # 映射 akshare 返回的列名到数据库字段
        column_mapping = {
            '日期': 'trade_date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount',
            '换手率': 'turnover',
            '振幅': 'amplitude',
            '涨跌幅': 'change_rate',
            '涨跌额': 'change_amount'
        }
        
        # 重命名列并添加股票代码
        processed_list = []
        for item in data_list:
            new_item = {}
            for old_col, new_col in column_mapping.items():
                if old_col in item:
                    new_item[new_col] = item[old_col]
            
            # 处理日期格式
            if 'trade_date' in new_item:
                if isinstance(new_item['trade_date'], str):
                    new_item['trade_date'] = datetime.datetime.strptime(new_item['trade_date'], '%Y-%m-%d').date()
            
            # 添加股票代码
            if ts_code:
                new_item['code'] = ts_code
            elif '股票代码' in item:
                new_item['code'] = item['股票代码']
            
            processed_list.append(new_item)
        
        # 批量插入到数据库
        result_ids = self.orm.batch_insert(processed_list)
        success_count = len([rid for rid in result_ids if rid is not None])
        
        logger.info(f"同步到数据库完成，成功: {success_count} 条")
        return success_count


if __name__ == "__main__":
    # 简单测试
    logger.info("测试 StockHistoryDataFetcher 模块")
    fetcher = StockHistoryDataFetcher(DB_CONFIG, REDIS_CONFIG)
    logger.info("StockHistoryDataFetcher 初始化成功")
