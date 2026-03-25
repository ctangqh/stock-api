import logging
from datetime import date, datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from conf.Config import DB_CONFIG
from data.stock_best_choose import StockBestChooseORM

router = APIRouter(prefix="/api/stock", tags=["stock_scan"])
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@router.get("/scan-results")
async def get_scan_results(
    date: str = Query(date.today().isoformat(), description="扫描日期，格式 yyyy-mm-dd，默认为今天"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数，默认 100，最大 1000")
) -> List[Dict[str, Any]]:
    """
    获取选股扫描结果
    
    参数:
        date: 可选，扫描日期，格式 yyyy-mm-dd，默认为今天
        limit: 可选，返回记录数，默认 100，最大 1000
        
    返回:
        选股结果列表
    """
    try:
        logger.info(f"开始处理 get_scan_results 请求，date={date}, limit={limit}")
        
        # 解析日期
        try:
            scan_date = datetime.fromisoformat(date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式不正确，应为 yyyy-mm-dd")
        
        # 验证 limit
        if limit > 1000:
            raise HTTPException(status_code=400, detail="limit 参数不能超过 1000")
        
        with StockBestChooseORM(DB_CONFIG) as orm:
            records = orm.get_by_scan_date(scan_date)
            # 限制返回数量
            records = records[:limit]
        
        logger.info(f"get_scan_results 请求处理成功，返回 {len(records)} 条记录")
        return records
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"处理 get_scan_results 请求失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
