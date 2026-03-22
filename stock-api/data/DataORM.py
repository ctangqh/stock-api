from data.news_driver import StockNewsDriverORM
from data.stock_recommend import StockRecommendPoolORM
from data.akshare_data import AkShareData
from data.prompt_memory_data import AiPromptMemoryORM
from conf.Config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

class DataORM:
    def __init__(self):
        logger.info("初始化 DataORM")
        self.news_orm = StockNewsDriverORM(DB_CONFIG)
        self.recommend_orm = StockRecommendPoolORM(DB_CONFIG)
        self.akshare = AkShareData()
        self.aiprompt = AiPromptMemoryORM(DB_CONFIG)

    def get_news_orm(self):
        return self.news_orm

    def get_recommend_orm(self):
        return self.recommend_orm

    def get_ai_prompt_orm(self):
        return self.aiprompt

    def get_akshare(self):
        return self.akshare
    
    def close(self):
        """关闭会话"""
        self.news_orm.close()
    
    def __enter__(self):
        """支持 with 语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.news_orm.close()
