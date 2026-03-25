from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()


class StockChooseStrategy(Base):
    __tablename__ = 'stock_choose_strategy'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    value = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, server_default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('name', name='_name_uc'),
    )


class StockChooseStrategyORM:
    def __init__(self, db_config: Dict):
        """
        初始化ORM操作类
        :param db_config: 数据库配置字典
        """
        logger.info("初始化 StockChooseStrategyORM")
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
        """创建数据表（仅测试环境用）"""
        Base.metadata.create_all(self.engine)

    def prepare_data_for_insert(self, data_list):
        cleaned_list = []
        for item in data_list:
            new_item = item.copy()
            if 'id' in new_item:
                del new_item['id']
            if 'created_at' in new_item:
                del new_item['created_at']
            if 'updated_at' in new_item:
                del new_item['updated_at']
            cleaned_list.append(new_item)
        return cleaned_list

    def batch_insert(self, data_list: List[Dict]) -> List[Optional[int]]:
        """
        批量插入或更新记录
        基于name判断冲突，冲突则更新，否则插入新记录
        :param data_list: 记录数据字典列表
        :return: 处理后的记录ID列表
        """
        logger.info(f"开始批量插入选股策略，共 {len(data_list)} 条")
        data_list = self.prepare_data_for_insert(data_list)
        session = self.Session()
        try:
            result_ids = []
            for data in data_list:
                existing = session.query(StockChooseStrategy).filter(
                    StockChooseStrategy.name == data['name']
                ).first()

                if existing:
                    logger.info(f"更新现有记录，name: {data['name']}")
                    for key, value in data.items():
                        setattr(existing, key, value)
                    result_ids.append(existing.id)
                else:
                    logger.info(f"插入新记录，name: {data['name']}")
                    new_record = StockChooseStrategy(**data)
                    session.add(new_record)
                    session.flush()
                    result_ids.append(new_record.id)

            session.commit()
            logger.info(f"批量插入选股策略完成，成功 {len([id for id in result_ids if id is not None])} 条")
            return result_ids

        except Exception as e:
            session.rollback()
            logger.exception(f"批量处理记录失败: {e}")
            return [None] * len(data_list)
        finally:
            session.close()

    def insert(self, data: Dict) -> Optional[int]:
        """
        插入新记录
        :param data: 记录数据字典
        :return: 插入记录的ID
        """
        session = self.Session()
        try:
            record = StockChooseStrategy(**data)
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
            record = session.query(StockChooseStrategy).filter(StockChooseStrategy.id == id).first()
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
            record = session.query(StockChooseStrategy).filter(StockChooseStrategy.id == id).first()
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
            record = session.query(StockChooseStrategy).filter(StockChooseStrategy.id == id).first()
            if record:
                return self._record_to_dict(record)
            return None
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return None
        finally:
            session.close()

    def get_all_active(self) -> List[Dict]:
        """
        获取所有激活状态的策略
        :return: 记录列表
        """
        session = self.Session()
        try:
            query = session.query(StockChooseStrategy).filter(StockChooseStrategy.status == 'active')
            records = query.all()
            return [self._record_to_dict(r) for r in records]
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return []
        finally:
            session.close()

    def get_by_name(self, name: str) -> Optional[Dict]:
        """
        根据名称获取策略
        :param name: 策略名称
        :return: 记录字典
        """
        session = self.Session()
        try:
            record = session.query(StockChooseStrategy).filter(StockChooseStrategy.name == name).first()
            if record:
                return self._record_to_dict(record)
            return None
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return None
        finally:
            session.close()

    def _record_to_dict(self, record) -> Dict:
        """
        将记录对象转换为字典
        :param record: StockChooseStrategy 对象
        :return: 字典
        """
        return {
            'id': record.id,
            'name': record.name,
            'value': record.value,
            'status': record.status,
            'created_at': record.created_at,
            'updated_at': record.updated_at
        }

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
    strategy_orm = StockChooseStrategyORM(db_config)

    # 创建表
    strategy_orm.create_table()

    # 插入示例数据
    data = {
        'name': '中等风险',
        'value': {
            'min_change_rate': 3.0,
            'max_change_rate': 6.0,
            'min_market_cap': 50,
            'max_market_cap': 800,
            'check_ma20': True,
            'check_macd': True,
            'check_recent_rise': True,
            'recent_days': 3
        },
        'status': 'active'
    }

    # 插入记录
    record_id = strategy_orm.insert(data)
    if record_id:
        print(f"成功插入记录，ID: {record_id}")

    # 查询记录
    record = strategy_orm.get_by_id(record_id)
    if record:
        print(f"查询到的记录: {record}")

    # 关闭连接
    strategy_orm.close()
