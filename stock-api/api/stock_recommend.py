from fastapi import APIRouter, Request, Query
from data.DataORM import DataORM
from data.stock_recommend import StockRecommendPool
from datetime import datetime, timedelta
import logging,json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stock", tags=["stock_recommend"])


@router.post("/recommend")
async def api_stock_recommend(request: Request):
    """
    处理推荐接口
    """
    try:
        logger.info("开始处理股票推荐请求")
        # 获取请求数据
        data = await request.json()
        logger.info(f"请求数据: {data}")
        if not data:
            return {"error": "请求数据不能为空"}, 400
        
        if not isinstance(data, list):
            logger.error(f"数据格式错误，期望列表，实际收到: {type(data)}")
            return {"error": "数据格式错误，需要数组格式"}, 400
 
        # 添加推荐日期
        date_now = datetime.now().date()
        in_datas = []
        for index, item_data in enumerate(data):
            item = json.loads(item_data)
            logger.info(f"处理第 {index}{item} 条数据")
            recommend_reason = item["recommend_reason"]
            code = item["code"]
            name = item["name"]
            # out_price = 0 if item["out_price"] is None else float(item["out_price"])
            in_price = 0
            # with DataORM() as orm:
            #     in_price = orm.get_akshare().get_stock_latest_price(code)
            in_data = {
                "name": name,
                "code": code,
                "in_price": 0,
                "in_date": date_now.strftime("%Y-%m-%d"),
                "recommend_date": date_now,
                "recommend_reason": recommend_reason,
                "recommend_status": "进行中",
                "out_price": 0,
                "out_date": (date_now + timedelta(days=3)),
                "profit_rate": 0,
            }
            in_datas.append(in_data)
        success_count = []
        logger.info("------ 入库数据 -------")
        logger.info(in_datas)
        with DataORM() as db:
            success_count = db.get_recommend_orm().batch_insert(in_datas)
        # 返回处理结果
        return {
            "message": f"处理完成，成功: {len(success_count)}"
        }
        
    except Exception as e:
        logger.exception(e)
        return {"error": f"处理失败: {str(e)}"}, 500

@router.get("/recommend/get")
async def api_stock_recommend_get(days: int = Query(default=6, alias="d")):
    """
    处理新闻线索接口
    接收新闻数据并批量插入到数据库
    """
    try:
        logger.info(f"开始获取最近 {days} 天的股票推荐")
        results = []
        with DataORM() as db:
            results = db.get_recommend_orm().search_recent_records(days)
        logger.info(f"获取股票推荐完成，共 {len(results)} 条")
        return {
            "message": f"处理完成，成功: {len(results)}",
            "data": results
        }
        
    except Exception as e:
        logger.exception(f"获取股票推荐失败: {e}")
        return {"error": f"处理失败: {str(e)}"}, 500

