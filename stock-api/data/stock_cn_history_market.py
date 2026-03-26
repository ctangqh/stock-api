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

    sync_date = Column(Date, primary_key=True)
    sync_time = Column(DateTime, nullable=True)
    data_date = Column(Date, nullable=False, index=True)
    stock_code = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100), nullable=True)
    current_price = Column(Numeric(10, 2), nullable=True)
    change_percent = Column(Numeric(8, 2), nullable=True)
    change_amount = Column(Numeric(20, 2), nullable=True)
    amplitude = Column(Numeric(8, 2), nullable=True)
    high_price = Column(Numeric(10, 2), nullable=True)
    low_price = Column(Numeric(10, 2), nullable=True)
    open_price = Column(Numeric(10, 2), nullable=True)
    pre_close = Column(Numeric(10, 2), nullable=True)
    volume = Column(BigInteger, nullable=True)
    turnover = Column(Numeric(20, 2), nullable=True)
    pe_ratio = Column(Numeric(10, 2), nullable=True)
    pb_ratio = Column(Numeric(10, 2), nullable=True)
    market_value = Column(Numeric(20, 2), nullable=True)
    circulating_market_value = Column(Numeric(20, 2), nullable=True)
    turnover_rate = Column(Numeric(8, 2), nullable=True)
    volume_ratio = Column(Numeric(8, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('stock_code', 'data_date', name='_stock_code_data_date_uc'),
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
        基于stock_code和data_date判断冲突，冲突则更新，否则插入新记录
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
                    StockCnHistoryMarket.stock_code == data['stock_code'],
                    StockCnHistoryMarket.data_date == data['data_date']
                ).first()

                if existing:
                    logger.info(f"更新现有记录，stock_code: {data['stock_code']}, data_date: {data['data_date']}")
                    for key, value in data.items():
                        setattr(existing, key, value)
                    result_ids.append(existing.sync_date)
                else:
                    logger.info(f"插入新记录，stock_code: {data['stock_code']}, data_date: {data['data_date']}")
                    new_record = StockCnHistoryMarket(**data)
                    session.add(new_record)
                    session.flush()
                    result_ids.append(new_record.sync_date)

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

    def get_by_id(self, id: date) -> Optional[Dict]:
        """
        根据ID获取记录
        :param id: 记录ID
        :return: 记录字典
        """
        session = self.Session()
        try:
            record = session.query(StockCnHistoryMarket).filter(StockCnHistoryMarket.sync_date == id).first()
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
            query = session.query(StockCnHistoryMarket).filter(StockCnHistoryMarket.stock_code == code)
            query = query.order_by(StockCnHistoryMarket.data_date.desc())
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
                StockCnHistoryMarket.stock_code == code,
                StockCnHistoryMarket.data_date >= start_date,
                StockCnHistoryMarket.data_date <= end_date
            )
            query = query.order_by(StockCnHistoryMarket.data_date)
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

    def get_by_data_date(self, data_date: date) -> List[Dict]:
        """
        按交易日期查询所有股票
        :param data_date: 交易日期
        :return: 记录列表
        """
        session = self.Session()
        try:
            # 使用原生SQL查询绕过主键问题（因为sync_date是主键，同一日期的多条记录会被合并）
            from sqlalchemy import text
            sql = text("""
                SELECT 
                    sync_date, sync_time, data_date, stock_code, stock_name,
                    current_price, change_percent, change_amount, amplitude,
                    high_price, low_price, open_price, pre_close, volume, turnover,
                    pe_ratio, pb_ratio, market_value, circulating_market_value,
                    turnover_rate, volume_ratio, created_at
                FROM stock_cn_history_market 
                WHERE data_date = :date
            """)
            result = session.execute(sql, {'date': data_date})
            
            records = []
            for row in result:
                # 构造字典
                record_dict = {
                    'sync_date': row[0],
                    'sync_time': row[1],
                    'data_date': row[2],
                    'stock_code': row[3],
                    'stock_name': row[4],
                    'current_price': row[5],
                    'change_percent': row[6],
                    'change_amount': row[7],
                    'amplitude': row[8],
                    'high_price': row[9],
                    'low_price': row[10],
                    'open_price': row[11],
                    'pre_close': row[12],
                    'volume': row[13],
                    'turnover': row[14],
                    'pe_ratio': row[15],
                    'pb_ratio': row[16],
                    'market_value': row[17],
                    'circulating_market_value': row[18],
                    'turnover_rate': row[19],
                    'volume_ratio': row[20],
                    'created_at': row[21]
                }
                # 转换为与_record_to_dict相同的格式
                records.append(self._row_to_dict(record_dict))
            
            return records
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            session.close()
    
    def _row_to_dict(self, row) -> Dict:
        """
        将原生SQL查询结果转换为字典
        :param row: 原生SQL查询结果字典
        :return: 格式化后的字典
        """
        return {
            'id': row['sync_date'],
            'code': row['stock_code'],
            'name': row['stock_name'],
            'data_date': row['data_date'],
            'open': float(row['open_price']) if row['open_price'] is not None else None,
            'high': float(row['high_price']) if row['high_price'] is not None else None,
            'low': float(row['low_price']) if row['low_price'] is not None else None,
            'close': float(row['current_price']) if row['current_price'] is not None else None,
            'volume': row['volume'],
            'amount': float(row['turnover']) if row['turnover'] is not None else None,
            'turnover': float(row['turnover_rate']) if row['turnover_rate'] is not None else None,
            'amplitude': float(row['amplitude']) if row['amplitude'] is not None else None,
            'change_percent': float(row['change_percent']) if row['change_percent'] is not None else None,
            'change_amount': float(row['change_amount']) if row['change_amount'] is not None else None,
            'market_value': float(row['market_value']) if row['market_value'] is not None else None,
            'circulating_market_value': float(row['circulating_market_value']) if row['circulating_market_value'] is not None else None,
            'ma5': None,
            'ma10': None,
            'ma20': None,
            'ma60': None,
            'macd_dif': None,
            'macd_dea': None,
            'macd_hist': None,
            'created_at': row['created_at']
        }

    def _record_to_dict(self, record) -> Dict:
        """
        将记录对象转换为字典
        :param record: StockCnHistoryMarket 对象
        :return: 字典
        """
        return {
            'id': record.sync_date,
            'code': record.stock_code,
            'name': record.stock_name,
            'data_date': record.data_date,
            'open': float(record.open_price) if record.open_price else None,
            'high': float(record.high_price) if record.high_price else None,
            'low': float(record.low_price) if record.low_price else None,
            'close': float(record.current_price) if record.current_price else None,
            'volume': record.volume,
            'amount': float(record.turnover) if record.turnover else None,
            'turnover': float(record.turnover_rate) if record.turnover_rate else None,
            'amplitude': float(record.amplitude) if record.amplitude else None,
            'change_percent': float(record.change_percent) if record.change_percent else None,
            'change_amount': float(record.change_amount) if record.change_amount else None,
            'market_value': float(record.market_value) if record.market_value else None,
            'circulating_market_value': float(record.circulating_market_value) if record.circulating_market_value else None,
            'ma5': None,  # Not present in actual table
            'ma10': None, # Not present in actual table
            'ma20': None, # Not present in actual table
            'ma60': None, # Not present in actual table
            'macd_dif': None, # Not present in actual table
            'macd_dea': None, # Not present in actual table
            'macd_hist': None, # Not present in actual table
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
