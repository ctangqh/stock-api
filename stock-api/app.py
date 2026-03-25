from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from get.astock_base import get_astock_index, get_usstock_index, get_cnstock_funds_flow, get_cnstock_trade_summary,cn_stock_bk_fund_flow
from util.ToolsUtil import ToolsUtil
from util.RedisUtil import RedisUtil
from api import news_driver, stock_recommend, prompt_memory, stock_real, stock_history, stock_scan
from conf.Config import FIELDS_FUNDS_FLOW_MAP
from data.data_format import prompt_stock_format
from datetime import datetime
import uvicorn
import os,json
import logging

logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(title="股票数据 API", version="1.0.0")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompt_memory.router)
app.include_router(news_driver.router)
app.include_router(stock_recommend.router)
app.include_router(stock_real.router)
app.include_router(stock_history.router)
app.include_router(stock_scan.router)

# 定义 API 路由
@app.get("/get_stock_summary")
async def api_get_astock_index(market: str = Query(default="cn", alias="m"), format: str = Query(default="json", alias="f")):
    """
    获取大盘数据
    
    参数:
        brief: 是否返回简洁版本，默认为 False
    返回:
        包含指数数据和总结的字典
    """
    try:
        logger.info(f"开始处理 get_stock_summary 请求, market={market}, format={format}")
        cn_data = []
        us_data = []
        cn_funds_flow_data = []
        bk_data = []
        with RedisUtil() as redis:
            # cn_trade_time = ToolsUtil.is_cn_stock_trading_time()
            cn_trade_time = False
            cn_ttl = 60*60*24
            # cn_trade_time = (not cn_trade_time)
            # us_trade_time = (not ToolsUtil.is_us_stock_trading_time())
            us_trade_time = False
            us_ttl = 60*60*24
            if market == "cn":
                logger.info("获取A股大盘数据")
                cn_data = redis.get_or_fetch("stock_summary_cnstock_index", get_astock_index, cn_ttl, cn_trade_time)
            if market == "us":
                logger.info("获取美股大盘数据")
                us_data = redis.get_or_fetch("stock_summary_usstock_index", get_usstock_index, us_ttl, us_trade_time)
            if market == "bk":
                logger.info("获取板块资金流向数据")
                bk_data = redis.get_or_fetch("stock_cn_bk_funds_flows", cn_stock_bk_fund_flow, cn_ttl, cn_trade_time)
            if market == "fund":
                logger.info("获取资金流向数据")
                cn_funds_flow_data = redis.get_or_fetch("stock_summary_cnstock_trade_summary", get_cnstock_trade_summary, cn_ttl, cn_trade_time)
        if format == "text":
            logger.info("返回文本格式数据")
            if market == "cn":
                return prompt_stock_format(cn_data, "cn")
            elif market == "us":
                return prompt_stock_format(us_data, "us")
            elif market == "bk":
                return prompt_stock_format(bk_data, "bk")
            else:
                return {}
        else:
            logger.info("返回JSON格式数据")
            return [*us_data, *cn_data, *cn_funds_flow_data]
        # cn_funds_flow_data = ToolsUtil.fields_data_map(cn_funds_flow_data, FIELDS_FUNDS_FLOW_MAP)
        # data = ToolsUtil.ticker_data_map([*cn_data, *us_data])
        # 返回结果
        
    except Exception as e:
        logger.exception(f"处理 get_stock_summary 请求失败: {e}")
        # 捕获异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_astock_funds_flow")
async def get_astock_funds_flow(brief: bool = False):
    """
    获取大盘数据
    
    参数:
        brief: 是否返回简洁版本，默认为 False
        
    返回:
        包含指数数据和总结的字典
    """
    try:
        logger.info(f"开始处理 get_astock_funds_flow 请求, brief={brief}")
        cn_funds_flow = []
        cn_trade_summary = []
        with RedisUtil() as redis:
            # cn_trade_time = not ToolsUtil.is_cn_stock_trading_time()
            # us_trade_time = not ToolsUtil.is_us_stock_trading_time()
            cn_trade_time = False
            us_trade_time = False
            logger.info("获取A股资金流向数据")
            cn_funds_flow = redis.get_or_fetch("stock_summary_cnstock_funds_flow", get_cnstock_funds_flow, 60*60*24, cn_trade_time)
            logger.info("获取A股交易汇总数据")
            cn_trade_summary = redis.get_or_fetch("stock_summary_cnstock_trade_summary", get_cnstock_trade_summary, 60*60*24, cn_trade_time)
        data = [*cn_funds_flow, *cn_trade_summary]
        # 返回结果
        logger.info("get_astock_funds_flow 请求处理成功")
        return {
            "code": 200,
            "message": "success",
            "data": ToolsUtil.fields_data_map(data, FIELDS_FUNDS_FLOW_MAP)
        }
    except Exception as e:
        logger.exception(f"处理 get_astock_funds_flow 请求失败: {e}")
        # 捕获异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_funds_flow")
async def api_get_funds_flow(date: str = Query(default=datetime.now().strftime("%Y%m%d"), alias="d"), 
    flow_direction: str = Query(default="in", alias="fd")) -> JSONResponse:
    try:
        logger.info(f"开始处理 get_funds_flow 请求, date={date}, flow_direction={flow_direction}")
        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建目标文件的相对路径
        file_path = os.path.join(current_dir, 'fund_flow_{1}_{0}.json'.format(date, flow_direction))
        logger.info(f"读取资金流向文件: {file_path}")
        data = None
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
        logger.info("get_funds_flow 请求处理成功")
        return JSONResponse(
            content=json.loads(data),
            media_type="application/json"
        )
    except FileNotFoundError:
        logger.error(f"文件未找到: {file_path}")
        return f"Error: file={file_path} not found"
    except Exception as e:
        logger.exception(f"读取文件失败: {e}")
        return f"Error reading file: {str(e)}"

@app.get("/get_prompt")
async def api_get_prompt():
    try:
        logger.info("开始处理 get_prompt 请求")
        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建目标文件的相对路径
        file_path = os.path.join(current_dir, 'prompt', 'prompt_stock_field.md')
        logger.info(f"读取提示文件: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.info("get_prompt 请求处理成功")
            return content
    except FileNotFoundError:
        logger.error("提示文件未找到: prompt_stock_field.md")
        return "Error: prompt_stock_field.md file not found"
    except Exception as e:
        logger.exception(f"读取提示文件失败: {e}")
        return f"Error reading file: {str(e)}"

# 启动应用
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
