from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class AiPromptMemory(Base):
    __tablename__ = 'ai_prompt_memory'
    
    id = Column(Integer, primary_key=True)
    context = Column(Text, nullable=False)
    prompt_class = Column(String(50))
    memory_date = Column(DateTime(timezone=True), default=func.now())

class AiPromptMemoryORM:
    def __init__(self, db_config: Dict):
        """
        初始化ORM操作类
        :param db_config: 数据库配置字典
        """
        logger.info("初始化 AiPromptMemoryORM")
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

    def insert(self, data: Dict) -> Optional[int]:
        """
        插入新记录
        :param data: 记录数据字典
        :return: 插入记录的ID
        """
        session = self.Session()
        try:
            record = AiPromptMemory(**data)
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
            record = session.query(AiPromptMemory).filter(AiPromptMemory.id == id).first()
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
            record = session.query(AiPromptMemory).filter(AiPromptMemory.id == id).first()
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
            record = session.query(AiPromptMemory).filter(AiPromptMemory.id == id).first()
            if record:
                return {
                    'id': record.id,
                    'context': record.context,
                    'prompt_class': record.prompt_class,
                    'memory_date': record.memory_date
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
            query = session.query(AiPromptMemory)
            if limit:
                query = query.limit(limit)
            records = query.all()
            return [{
                'id': r.id,
                'context': r.context,
                'prompt_class': r.prompt_class,
                'memory_date': r.memory_date
            } for r in records]
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return []
        finally:
            session.close()
            
    def search(self, conditions: Dict, limit: Optional[int] = 1) -> List[Dict]:
        """
        根据条件搜索记录
        :param conditions: 搜索条件字典
        :param limit: 可选，限制返回记录数
        :return: 符合条件的记录列表
        """
        session = self.Session()
        try:
            query = session.query(AiPromptMemory)
            
            for key, value in conditions.items():
                if hasattr(AiPromptMemory, key):
                    query = query.filter(getattr(AiPromptMemory, key) == value)
                    
            if limit:
                query = query.order_by(AiPromptMemory.memory_date.desc()).limit(limit)
            records = query.all()
            return [{
                'id': r.id,
                'context': r.context,
                'prompt_class': r.prompt_class,
                'memory_date': r.memory_date
            } for r in records]
        except Exception as e:
            logger.error(f"搜索记录失败: {e}")
            return []
        finally:
            session.close()

    def search_by_class(self, class_name: str, limit: Optional[int] = None) -> List[Dict]:
        """
        根据分类搜索记录
        :param class_name: 分类名称
        :param limit: 可选，限制返回记录数
        :return: 符合条件的记录列表
        """
        return self.search({'prompt_class': class_name}, limit)

    def search_recent_records(
        self, 
        days: int = 6,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        查找近 days 天内的记录
        :param days: 查询最近多少天，默认为 6
        :param end_date: 查询的截止日期（包含当天），默认为今天
        :return: 符合条件的记录列表
        """
        from datetime import timedelta
        
        session = self.Session()
        try:
            if end_date is None:
                end_date = datetime.now()
            
            start_date = end_date - timedelta(days=days)
            
            records = session.query(AiPromptMemory).filter(
                AiPromptMemory.memory_date >= start_date,
                AiPromptMemory.memory_date <= end_date
            ).all()
            
            return [{
                'id': r.id,
                'context': r.context,
                'prompt_class': r.prompt_class,
                'memory_date': r.memory_date
            } for r in records]
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return []
        finally:
            session.close()

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
    ai_prompt_orm = AiPromptMemoryORM(db_config)
    
    # 创建表
    ai_prompt_orm.create_table()
    
    # 插入示例数据
    data = {
        'context': '这是一个示例上下文',
        'class_name': '示例分类'
    }
    
    # 插入记录
    record_id = ai_prompt_orm.insert(data)
    if record_id:
        print(f"成功插入记录，ID: {record_id}")
    
    # 查询记录
    record = ai_prompt_orm.get_by_id(record_id)
    if record:
        print(f"查询到的记录: {record}")
    
    # 关闭连接
    ai_prompt_orm.close()

