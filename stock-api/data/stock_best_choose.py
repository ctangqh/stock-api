from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()


class StockBestChoose(Base):
    __tablename__ = 'stock_best_choose'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    scan_date = Column(Date, nullable=False, index=True)
    choose_reason = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StockBestChooseORM:
    def __init__(self, db_config: Dict):
        """
        初始化ORM操作类
        :param db_config: 数据库配置字典
        """
        logger.info("初始化 StockBestChooseORM")
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
            cleaned_list.append(new_item)
        return cleaned_list

    def batch_insert(self, data_list: List[Dict]) -> List[Optional[int]]:
        """
        批量插入或更新记录
        :param data_list: 记录数据字典列表
        :return: 处理后的记录ID列表
        """
        logger.info(f"开始批量插入选股结果，共 {len(data_list)} 条")
        data_list = self.prepare_data_for_insert(data_list)
        session = self.Session()
        try:
            result_ids = []
            for data in data_list:
                new_record = StockBestChoose(**data)
                session.add(new_record)
                session.flush()
                result_ids.append(new_record.id)

            session.commit()
            logger.info(f"批量插入选股结果完成，成功 {len([id for id in result_ids if id is not None])} 条")
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
            record = StockBestChoose(**data)
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
            record = session.query(StockBestChoose).filter(StockBestChoose.id == id).first()
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
            record = session.query(StockBestChoose).filter(StockBestChoose.id == id).first()
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
            record = session.query(StockBestChoose).filter(StockBestChoose.id == id).first()
            if record:
                return self._record_to_dict(record)
            return None
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return None
        finally:
            session.close()

    def get_by_scan_date(self, scan_date) -> List[Dict]:
        """
        根据扫描日期查询
        :param scan_date: 扫描日期
        :return: 记录列表
        """
        session = self.Session()
        try:
            query = session.query(StockBestChoose).filter(StockBestChoose.scan_date == scan_date)
            records = query.all()
            return [self._record_to_dict(r) for r in records]
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return []
        finally:
            session.close()

    def get_recent_days(self, days: int = 3) -> List[Dict]:
        """
        查询最近几天的数据
        :param days: 天数，默认 3 天
        :return: 记录列表，按创建时间倒序排列
        """
        from datetime import date, timedelta
        session = self.Session()
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            query = session.query(StockBestChoose).filter(
                StockBestChoose.scan_date >= start_date,
                StockBestChoose.scan_date <= end_date
            ).order_by(StockBestChoose.created_at.desc())
            
            records = query.all()
            return [self._record_to_dict(r) for r in records]
        except Exception as e:
            logger.error(f"查询最近几天数据失败: {e}")
            return []
        finally:
            session.close()

    def _record_to_dict(self, record) -> Dict:
        """
        将记录对象转换为字典
        :param record: StockBestChoose 对象
        :return: 字典
        """
        return {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'scan_date': record.scan_date,
            'choose_reason': record.choose_reason,
            'created_at': record.created_at
        }

    def close(self):
        """关闭数据库连接"""
        self.Session.remove()
        
    def __enter__(self):
        """支持 with 语句"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.close()


# 使用示例
if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'database': 'your_database',
        'user': 'your_username',
        'password': 'your_password'
    }

    # 创建ORM操作类实例
    best_choose_orm = StockBestChooseORM(db_config)

    # 创建表
    best_choose_orm.create_table()

    # 插入示例数据
    from datetime import date
    data = {
        'code': '000001.SZ',
        'name': '平安银行',
        'scan_date': date.today(),
        'choose_reason': {
            'strategy': '中等风险',
            'score': 85
        }
    }

    # 插入记录
    record_id = best_choose_orm.insert(data)
    if record_id:
        print(f"成功插入记录，ID: {record_id}")

    # 查询记录
    record = best_choose_orm.get_by_id(record_id)
    if record:
        print(f"查询到的记录: {record}")

    # 关闭连接
    best_choose_orm.close()
