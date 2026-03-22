import logging
from fastapi import APIRouter, Request, Query
from data.DataORM import DataORM
from data.stock_real import StockDataParser
from datetime import datetime, timedelta
from get.astock_base import get_astock_price

router = APIRouter(prefix="/api/stock", tags=["stock_real"])
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@router.get("/price")
async def api_stock_real(symbol: str = Query(default='sz000001', alias="s")):
    # http://qt.gtimg.cn/q=sh600941
    return get_astock_price(symbol)
    
