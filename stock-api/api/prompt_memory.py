from typing import Annotated
from fastapi import APIRouter, Request, Query, Form, Body
from data.DataORM import DataORM
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/prompt", tags=["prompt_memory"])

@router.post("/in")
async def api_prompt_in(
        context: str = Form(...),
        prompt_class: str = Form(default='涨停聚焦') # 可选参数
    ):
    """
    处理推荐接口
    """
    try:
        logger.info("开始处理提示记忆保存请求")
        if not context:
            logger.error("请求数据不能为空")
            return {"error": "请求数据不能为空"}, 400
            
        prompt_class = "股票分析" if prompt_class is None else prompt_class
        logger.info(f"提示分类: {prompt_class}")
        
        in_data = {
            "context": context,
            "prompt_class": prompt_class
        }
        success_count = 0
        logger.info("开始保存提示记忆")
        with DataORM() as db:
            success_count = db.get_ai_prompt_orm().insert(in_data)
        # 返回处理结果
        logger.info(f"提示记忆保存完成，成功: {success_count}")
        return {
            "message": f"处理完成，成功: {success_count}"
        }
        
    except Exception as e:
        logger.exception(f"处理提示记忆保存请求失败: {e}")
        return {"error": f"处理失败: {str(e)}"}, 500

@router.get("/get")
async def api_prompt_get(cls_name: str = Query(default="涨停聚焦", alias="cls")):
    """
    处理新闻线索接口
    接收新闻数据并批量插入到数据库
    """
    try:
        logger.info(f"开始获取提示记忆，分类: {cls_name}")
        results = []
        with DataORM() as db:
            data = {
                "prompt_class": cls_name
            }
            results = db.get_ai_prompt_orm().search(data)
        logger.info(f"获取提示记忆完成，共 {len(results)} 条")
        return {
            "message": f"处理完成，成功: {len(results)}",
            "data": results[0]["context"]
        }
        
    except Exception as e:
        logger.exception(f"获取提示记忆失败: {e}")
        return {"error": f"处理失败: {str(e)}"}, 500
