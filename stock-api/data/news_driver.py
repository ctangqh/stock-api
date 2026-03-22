from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict
from util.PgDBUtil import PgDBUtil
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class StockNewsDriver(Base):
    __tablename__ = 'stock_news_driver'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    industry = Column(String(300))
    relation_industry_chains = Column(Text)
    relation = Column(String(50))
    relation_weight = Column(String(10))
    recommend_date = Column(Date)
    created_at = Column(DateTime, default=func.now())

class StockNewsDriverORM:
    def __init__(self, db_config: Dict):
        """
        初始化ORM操作类
        :param db_config: 数据库配置字典
        """
        logger.info("初始化 StockNewsDriverORM")
        self.db_config = db_config
        
        # 创建SQLAlchemy引擎
        self.engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        
        # 创建会话工厂
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
    def create_table(self):
        """创建数据表"""
        Base.metadata.create_all(self.engine)

    def batch_insert(self, data_list: List[Dict]) -> List[Optional[int]]:
        """
        批量插入或更新记录
        基于code和recommend_date判断冲突，冲突则更新，否则插入新记录
        :param data_list: 记录数据字典列表
        :return: 处理后的记录ID列表
        """
        logger.info(f"开始批量插入新闻线索，共 {len(data_list)} 条")
        data_list = self.prepare_data_for_insert(data_list)
        logger.debug(f"准备插入的数据: {data_list}")
        session = self.Session()
        try:
            result_ids = []
            for data in data_list:
                # 检查是否存在相同code和recommend_date的记录
                existing = session.query(StockNewsDriver).filter(
                    StockNewsDriver.code == data['code'],
                    func.date(StockNewsDriver.recommend_date) == data['recommend_date']
                ).first()
                
                if existing:
                    # 更新现有记录
                    logger.info(f"更新现有记录，code: {data['code']}, recommend_date: {data['recommend_date']}")
                    for key, value in data.items():
                        setattr(existing, key, value)
                    result_ids.append(existing.id)
                else:
                    # 插入新记录
                    logger.info(f"插入新记录，code: {data['code']}, recommend_date: {data['recommend_date']}")
                    new_record = StockNewsDriver(**data)
                    session.add(new_record)
                    session.flush()  # 获取新记录的ID
                    result_ids.append(new_record.id)
            
            session.commit()
            logger.info(f"批量插入新闻线索完成，成功 {len([id for id in result_ids if id is not None])} 条")
            return result_ids
            
        except Exception as e:
            session.rollback()
            logger.exception(f"批量处理记录失败: {e}")
            return [None] * len(data_list)
        finally:
            session.close()


    def prepare_data_for_insert(self, data_list):
        cleaned_list = []
        for item in data_list:
            # 复制字典以免修改原数据（可选）
            new_item = item.copy()
            # 如果存在 id 键，将其移除
            if 'id' in new_item:
                del new_item['id']
            # 也可以移除 created_at，让数据库使用默认值
            if 'created_at' in new_item:
                del new_item['created_at']
            cleaned_list.append(new_item)
        return cleaned_list


    def insert(self, data: Dict) -> Optional[int]:
        """
        插入新记录
        :param data: 记录数据字典
        :return: 插入记录的ID
        """
        session = self.Session()
        try:
            record = StockNewsDriver(**data)
            session.add(record)
            session.commit()
            return record.id
        except Exception as e:
            session.rollback()
            logger.error(f"插入记录失败: {e}")
            return None
        finally:
            session.close()
            
    def update(self, id: int, data: Dict) -> bool:
        """
        更新记录
        :param id: 记录ID
        :param data: 更新数据字典
        :return: 更新是否成功
        """
        session = self.Session()
        try:
            record = session.query(StockNewsDriver).filter(StockNewsDriver.id == id).first()
            if record:
                for key, value in data.items():
                    setattr(record, key, value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新记录失败: {e}")
            return False
        finally:
            session.close()
            
    def delete(self, id: int) -> bool:
        """
        删除记录
        :param id: 记录ID
        :return: 删除是否成功
        """
        session = self.Session()
        try:
            record = session.query(StockNewsDriver).filter(StockNewsDriver.id == id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"删除记录失败: {e}")
            return False
        finally:
            session.close()
            
    def get_by_id(self, id: int) -> Optional[Dict]:
        """
        根据ID获取记录
        :param id: 记录ID
        :return: 记录字典
        """
        session = self.Session()
        try:
            record = session.query(StockNewsDriver).filter(StockNewsDriver.id == id).first()
            if record:
                return {
                    'id': record.id,
                    'name': record.name,
                    'code': record.code,
                    'industry': record.industry,
                    'relation_industry_chains': record.relation_industry_chains,
                    'relation': record.relation,
                    'relation_weight': record.relation_weight,
                    'recommend_date': record.recommend_date,
                    'created_at': record.created_at
                }
            return None
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return None
        finally:
            session.close()
            
    def get_all(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取所有记录
        :param limit: 可选，限制返回记录数
        :return: 记录列表
        """
        session = self.Session()
        try:
            query = session.query(StockNewsDriver)
            if limit:
                query = query.limit(limit)
            records = query.all()
            return [{
                'id': r.id,
                'name': r.name,
                'code': r.code,
                'industry': r.industry,
                'relation_industry_chains': r.relation_industry_chains,
                'relation': r.relation,
                'relation_weight': r.relation_weight,
                'recommend_date': r.recommend_date,
                'created_at': r.created_at
            } for r in records]
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return []
        finally:
            session.close()
            
    def search(self, conditions: Dict, limit: Optional[int] = None) -> List[Dict]:
        """
        根据条件搜索记录
        :param conditions: 搜索条件字典
        :param limit: 可选，限制返回记录数
        :return: 符合条件的记录列表
        """
        session = self.Session()
        try:
            query = session.query(StockNewsDriver)
            
            for key, value in conditions.items():
                if hasattr(StockNewsDriver, key):
                    query = query.filter(getattr(StockNewsDriver, key) == value)
                    
            if limit:
                query = query.limit(limit)
                
            records = query.all()
            return [{
                'id': r.id,
                'name': r.name,
                'code': r.code,
                'industry': r.industry,
                'relation_industry_chains': r.relation_industry_chains,
                'relation': r.relation,
                'relation_weight': r.relation_weight,
                'recommend_date': r.recommend_date,
                'created_at': r.created_at
            } for r in records]
        except Exception as e:
            logger.error(f"搜索记录失败: {e}")
            return []
        finally:
            session.close()

    def search_recent_records(
        self, 
        days: int = 6,  # 新增参数，默认为6天
        end_date: Optional[date] = None # 可选：指定截止日期，默认为今天
    ) -> List[StockNewsDriver]:
        """
        查找近 days 天内的记录。
        
        Args:
            session: 数据库会话
            days: 查询最近多少天，默认为 6
            end_date: 查询的截止日期（包含当天），默认为今天。如果指定，则查询 [end_date - days, end_date]
        
        Returns:
            List[StockNewsDriver]: 查询结果列表
        """
        session = self.Session()
        # 1. 确定截止日期（默认为今天）
        if end_date is None:
            end_date = datetime.now().date()
        
        # 2. 计算起始日期
        start_date = end_date - timedelta(days=days)
        
        # 3. 执行查询
        # 逻辑：recommend_date >= 起始日期 AND recommend_date <= 截止日期
        results = session.query(StockNewsDriver).filter(
            StockNewsDriver.recommend_date >= start_date,
            StockNewsDriver.recommend_date <= end_date
        ).all()
        
        return results

    def close(self):
        """关闭数据库连接"""
        self.Session.remove()

# 使用示例
if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'database': 'your_database',
        'user': 'your_username',
        'password': 'your_password'
    }
    
    # 创建ORM操作类实例
    stock_news_orm = StockNewsDriverORM(db_config)
    
    # 创建表
    stock_news_orm.create_table()
    
    # 插入示例数据
    data = {
        'name': '奥飞娱乐',
        'code': '002292.SZ',
        'industry': '文化传媒/动漫IP',
        'relation_industry_chains': '拥有大量原创动漫IP资源',
        'relation': '下游',
        'relation_weight': '中',
        'recommend_date': datetime.now().date()
    }
    
    # 插入记录
    record_id = stock_news_orm.insert(data)
    if record_id:
        print(f"成功插入记录，ID: {record_id}")
    
    # 查询记录
    record = stock_news_orm.get_by_id(record_id)
    if record:
        print(f"查询到的记录: {record}")
    
    # 关闭连接
    stock_news_orm.close()

