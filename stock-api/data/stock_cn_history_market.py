from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Numeric, BigInteger, func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()


class StockCnHistoryMarket(Base):
    __tablename__ = 'stock_cn_history_market'

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    trade_date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 2), nullable=True)
    high = Column(Numeric(10, 2), nullable=True)
    low = Column(Numeric(10, 2), nullable=True)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=True)
    amount = Column(Numeric(20, 2), nullable=True)
    turnover = Column(Numeric(8, 2), nullable=True)
    amplitude = Column(Numeric(8, 2), nullable=True)
    change_rate = Column(Numeric(8, 2), nullable=True)
    change_amount = Column(Numeric(20, 2), nullable=True)
    ma5 = Column(Numeric(10, 2), nullable=True)
    ma10 = Column(Numeric(10, 2), nullable=True)
    ma20 = Column(Numeric(10, 2), nullable=True)
    ma60 = Column(Numeric(10, 2), nullable=True)
    macd_dif = Column(Numeric(10, 2), nullable=True)
    macd_dea = Column(Numeric(10, 2), nullable=True)
    macd_hist = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('code', 'trade_date', name='_code_trade_date_uc'),
    )


class StockCnHistoryMarketORM:
    def __init__(self, db_config: Dict):
        """
        初始化ORM操作类
        :param db_config: 数据库配置字典
        """
        logger.info("初始化 StockCnHistoryMarketORM")
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
        基于code和trade_date判断冲突，冲突则更新，否则插入新记录
        :param data_list: 记录数据字典列表
        :return: 处理后的记录ID列表
        """
        logger.info(f"开始批量插入股票历史行情，共 {len(data_list)} 条")
        data_list = self.prepare_data_for_insert(data_list)
        session = self.Session()
        try:
            result_ids = []
            for data in data_list:
                existing = session.query(StockCnHistoryMarket).filter(
                    StockCnHistoryMarket.code == data['code'],
                    StockCnHistoryMarket.trade_date == data['trade_date']
                ).first()

                if existing:
                    logger.info(f"更新现有记录，code: {data['code']}, trade_date: {data['trade_date']}")
                    for key, value in data.items():
                        setattr(existing, key, value)
                    result_ids.append(existing.id)
                else:
                    logger.info(f"插入新记录，code: {data['code']}, trade_date: {data['trade_date']}")
                    new_record = StockCnHistoryMarket(**data)
                    session.add(new_record)
                    session.flush()
                    result_ids.append(new_record.id)

            session.commit()
            logger.info(f"批量插入股票历史行情完成，成功 {len([id for id in result_ids if id is not None])} 条")
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
            record = StockCnHistoryMarket(**data)
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
            record = session.query(StockCnHistoryMarket).filter(StockCnHistoryMarket.id == id).first()
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
            record = session.query(StockCnHistoryMarket).filter(StockCnHistoryMarket.id == id).first()
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
            record = session.query(StockCnHistoryMarket).filter(StockCnHistoryMarket.id == id).first()
            if record:
                return self._record_to_dict(record)
            return None
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return None
        finally:
            session.close()

    def get_by_code(self, code: str, limit: Optional[int] = None) -> List[Dict]:
        """
        按代码查询，按日期排序
        :param code: 股票代码
        :param limit: 可选，限制返回记录数
        :return: 记录列表
        """
        session = self.Session()
        try:
            query = session.query(StockCnHistoryMarket).filter(StockCnHistoryMarket.code == code)
            query = query.order_by(StockCnHistoryMarket.trade_date.desc())
            if limit:
                query = query.limit(limit)
            records = query.all()
            return [self._record_to_dict(r) for r in records]
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return []
        finally:
            session.close()

    def get_by_code_and_date_range(self, code: str, start_date: date, end_date: date) -> List[Dict]:
        """
        按代码和日期范围查询
        :param code: 股票代码
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 记录列表
        """
        session = self.Session()
        try:
            query = session.query(StockCnHistoryMarket).filter(
                StockCnHistoryMarket.code == code,
                StockCnHistoryMarket.trade_date >= start_date,
                StockCnHistoryMarket.trade_date <= end_date
            )
            query = query.order_by(StockCnHistoryMarket.trade_date)
            records = query.all()
            return [self._record_to_dict(r) for r in records]
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return []
        finally:
            session.close()

    def get_latest_by_code(self, code: str, days: int = 60) -> List[Dict]:
        """
        获取最近 N 天数据
        :param code: 股票代码
        :param days: 天数，默认60天
        :return: 记录列表
        """
        session = self.Session()
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            return self.get_by_code_and_date_range(code, start_date, end_date)
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return []
        finally:
            session.close()

    def _record_to_dict(self, record) -> Dict:
        """
        将记录对象转换为字典
        :param record: StockCnHistoryMarket 对象
        :return: 字典
        """
        return {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'trade_date': record.trade_date,
            'open': float(record.open) if record.open else None,
            'high': float(record.high) if record.high else None,
            'low': float(record.low) if record.low else None,
            'close': float(record.close) if record.close else None,
            'volume': record.volume,
            'amount': float(record.amount) if record.amount else None,
            'turnover': float(record.turnover) if record.turnover else None,
            'amplitude': float(record.amplitude) if record.amplitude else None,
            'change_rate': float(record.change_rate) if record.change_rate else None,
            'change_amount': float(record.change_amount) if record.change_amount else None,
            'ma5': float(record.ma5) if record.ma5 else None,
            'ma10': float(record.ma10) if record.ma10 else None,
            'ma20': float(record.ma20) if record.ma20 else None,
            'ma60': float(record.ma60) if record.ma60 else None,
            'macd_dif': float(record.macd_dif) if record.macd_dif else None,
            'macd_dea': float(record.macd_dea) if record.macd_dea else None,
            'macd_hist': float(record.macd_hist) if record.macd_hist else None,
            'created_at': record.created_at
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
    stock_history_orm = StockCnHistoryMarketORM(db_config)

    # 创建表
    stock_history_orm.create_table()

    # 插入示例数据
    data = {
        'code': '000001.SZ',
        'name': '平安银行',
        'trade_date': date.today(),
        'open': 10.50,
        'high': 10.80,
        'low': 10.20,
        'close': 10.60,
        'volume': 1000000,
        'amount': 10600000.00,
        'turnover': 2.5,
        'amplitude': 5.71,
        'change_rate': 0.95,
        'change_amount': 0.10
    }

    # 插入记录
    record_id = stock_history_orm.insert(data)
    if record_id:
        print(f"成功插入记录，ID: {record_id}")

    # 查询记录
    record = stock_history_orm.get_by_id(record_id)
    if record:
        print(f"查询到的记录: {record}")

    # 关闭连接
    stock_history_orm.close()
