from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()


class StockCnInfo(Base):
    __tablename__ = 'stock_cn_info'

    code = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    code_cn = Column(String(20))
    market_cap = Column(Numeric)


class StockCnInfoORM:
    def __init__(self, db_config: Dict):
        logger.info("初始化 StockCnInfoORM")
        self.db_config = db_config

        self.engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )

        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def get_by_code(self, code: str) -> Optional[Dict]:
        session = self.Session()
        try:
            record = session.query(StockCnInfo).filter(StockCnInfo.code == code).first()
            if record:
                return self._record_to_dict(record)
            return None
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return None
        finally:
            session.close()

    def batch_get_by_codes(self, codes: List[str]) -> Dict[str, Dict]:
        session = self.Session()
        try:
            records = session.query(StockCnInfo).filter(StockCnInfo.code.in_(codes)).all()
            result = {}
            for record in records:
                result[record.code] = self._record_to_dict(record)
            return result
        except Exception as e:
            logger.error(f"批量查询记录失败: {e}")
            return {}
        finally:
            session.close()

    def _record_to_dict(self, record) -> Dict:
        return {
            'code': record.code,
            'name': record.name,
            'code_cn': record.code_cn,
            'market_cap': float(record.market_cap) if record.market_cap else None
        }

    def close(self):
        self.Session.remove()
