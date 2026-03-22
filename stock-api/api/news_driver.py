from fastapi import APIRouter, Request, Query
from data.DataORM import DataORM
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/news", tags=["news_driver"])


@router.post("/clue")
async def api_news_clue(request: Request):
    """
    处理新闻线索接口
    接收新闻数据并批量插入到数据库
    """
    try:
        logger.info("开始处理新闻线索请求")
        # 获取请求数据
        data = await request.json()
        logger.info(f"请求数据: {data}")
        if not data:
            logger.error("请求数据不能为空")
            return {"error": "请求数据不能为空"}, 400
            
        # 验证数据格式
        if not isinstance(data, list):
            logger.error(f"数据格式错误，期望列表，实际收到: {type(data)}")
            return {"error": "数据格式错误，需要数组格式"}, 400
            
        # 添加推荐日期
        date_now = str(datetime.now().date())
        for item in data:
            item["recommend_date"] = date_now
        
        result_ids = []
        logger.info("开始批量插入新闻线索数据")
        with DataORM() as db:
            result_ids = db.get_news_orm().batch_insert(data)
        # 返回处理结果
        success_count = sum(1 for id in result_ids if id is not None)
        logger.info(f"新闻线索处理完成，成功: {success_count}/{len(data)}")
        return {
            "message": f"处理完成，成功: {success_count}/{len(data)}",
            "ids": result_ids
        }
        
    except Exception as e:
        logger.exception(f"处理新闻线索请求失败: {e}")
        return {"error": f"处理失败: {str(e)}"}, 500

@router.get("/clue/get")
async def api_news_clue_get(days: int = Query(default=6, alias="d")):
    """
    处理新闻线索接口
    接收新闻数据并批量插入到数据库
    """
    try:
        logger.info(f"开始获取最近 {days} 天的新闻线索")
        results = []
        with DataORM() as db:
            results = db.get_news_orm().search_recent_records(days)
        logger.info(f"获取新闻线索完成，共 {len(results)} 条")
        return {
            "message": f"处理完成，成功: {len(results)}",
            "data": results
        }
        
    except Exception as e:
        logger.exception(f"获取新闻线索失败: {e}")
        return {"error": f"处理失败: {str(e)}"}, 500

