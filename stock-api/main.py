from job.daily import process_daily_data
from util.RedisUtil import RedisUtil
from util.ToolsUtil import ToolsUtil
from conf.Config import FIELDS_FUNDS_FLOW_MAP
from get.astock_base import get_astock_index, get_usstock_index, get_cnstock_funds_flow, get_cnstock_trade_summary
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("启动主程序")
    # process_daily_data()
    # cn_data = []
    # us_data = []
    # with RedisUtil() as redis:
    #     cn_data = redis.get_or_fetch("stock_summary_cnstock_index", get_astock_index, 60*60*24)
    #     us_data = redis.get_or_fetch("stock_summary_usstock_index", get_usstock_index, 60*60*24)
    # data = [*cn_data, *us_data]
    # index_data_list = ToolsUtil.ticker_data_map(data)
    # print(index_data_list)
    cn_trade_time = not ToolsUtil.is_cn_stock_trading_time()
    us_trade_time = not ToolsUtil.is_us_stock_trading_time()
    cn_trade_time = True
    us_trade_time = True
    logger.info(f"交易时间设置 - A股: {cn_trade_time}, 美股: {us_trade_time}")
    with RedisUtil() as redis:
        cn_data = redis.get_or_fetch("stock_summary_cnstock_index", get_astock_index, 60*60*24, cn_trade_time)
        us_data = redis.get_or_fetch("stock_summary_usstock_index", get_usstock_index, 60*60*24, us_trade_time)
        cn_funds_flow = redis.get_or_fetch("stock_summary_cnstock_funds_flow", get_cnstock_funds_flow, 60*60*24, cn_trade_time)
        data = [*cn_data, *us_data]
        data = ToolsUtil.ticker_data_map(data)
        data = [*ToolsUtil.fields_data_map(cn_funds_flow, FIELDS_FUNDS_FLOW_MAP), *data]
        logger.info(f"主程序执行完成，数据: {data}")