from util.PgDBUtil import PgDBUtil
from util.HttpUtil import HttpUtil
from conf.Config import DB_CONFIG as db_conf
from data.fund_flow_data import batch_upsert_stock_data,prepare_stock_data
import akshare as ak
import pandas as pd
import re
import json
import time
import random
from datetime import datetime
import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_individual_fund_flow_data(sort_type, pages):
    url = "https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery11230919858424235644_1770456637056&fid=f184&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13"
    # url = "https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112306545370547060039_1770687641621&fid=f184&po=0&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13"
    base_url, params = HttpUtil.url2param(url)
    default_headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Content-Type": "application/javascript; charset=UTF-8",
        "Host": "push2.eastmoney.com",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest":"script",
        "Sec-Fetch-Mode":"no-cors", 
        "Sec-Fetch-Site":"same-site",
        "Sec-Ch-Ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "Referer": "https://data.eastmoney.com/zjlx/detail.html"
    }
    cookie_str = "qgqp_b_id=476adfb9b95b9c52be2a02dbc2fe5005; st_nvi=ZaT6vtQIJcsU1WERopjqY0258; nid18=0c761ad2ddf5902ad2bb97b3d8031392; nid18_create_time=1768136306577; gviem=IaR46LxELHLsqxDEao4hY0821; gviem_create_time=1768136306578; fullscreengg=1; fullscreengg2=1; st_si=56798892871416; websitepoptg_api_time=1770455742795; st_asi=delete; st_pvi=96913291039558; st_sp=2026-01-11%2020%3A58%3A23; st_inirUrl=https%3A%2F%2Fwww.google.com.hk%2F; st_sn=15; st_psi=20260207173021173-113200313000-8368862338"
    default_cookies= HttpUtil.cookie_translate(cookie_str)
    http_util = HttpUtil(base_url, default_headers, default_cookies, 30)
    fund_flow_list = []
    with http_util:
        for i in pages:
            if sort_type == 'in':
                params['po'] = 1
            else:
                params['po'] = 0
            params['pn'] = i
            time.sleep(random.randint(1, 10))
            try:
            # 发送 GET 请求
                response = http_util.get("/api/qt/clist/get", params=params)
                data = extract_json_from_callback(response.text)['data']['diff']
                logger.info(f"GET 请求状态码: {response.status_code}")
            except Exception as e:
                logger.exception(f"GET 请求异常: {e.__context__}")
                continue
            logger.info(f"GET 获取到数据 {len(data)} 条")
            fund_flow_list.extend(data)
    with PgDBUtil(**db_conf) as db:
        file_name = 'fund_flow_{0}_{1}.json'.format(datetime.now().strftime("%Y%m%d"), sort_type)
        pd.DataFrame(fund_flow_list).to_json(file_name, orient='records', force_ascii=False)
        # result = batch_upsert_stock_data(db, prepare_stock_data(fund_flow_list))
        # print(f"数据插入完成，累计入库 {result} 条")
    # 板块资金流向
    # https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112303094303797946032_1770480427633&fid=f184&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13

def extract_jquery_callback(callback_str):
    """
    从 jQuery 回调函数中提取文本内容
    
    参数:
    callback_str -- jQuery 回调函数字符串，格式为 "jQuery11230919858424235644_1770456637056(text);"
    
    返回:
    提取的文本内容
    """
    # 使用正则表达式匹配 jQuery 回调函数
    pattern = r'jQuery\d+_\d+\((.*?)\);'
    match = re.search(pattern, callback_str)
    if match:
        # 提取匹配的文本
        text = match.group(1)
        return text
    else:
        return None

def extract_json_from_callback(callback_str):
    """
    从 jQuery 回调函数中提取 JSON 数据
    
    参数:
    callback_str -- jQuery 回调函数字符串，格式为 "jQuery11230919858424235644_1770456637056(json);"
    
    返回:
    提取的 JSON 数据（已转换为 Python 字典）
    """
    # 提取文本内容
    text = extract_jquery_callback(callback_str)
    
    if text:
        try:
            # 将 JSON 字符串转换为 Python 字典
            return json.loads(text)
        except json.JSONDecodeError:
            # 如果不是有效的 JSON，返回原始文本
            return text
    else:
        return None

def process_month_data():
    logger.info(f'开始处理月度数据')
    stock_info = ak.stock_info_a_code_name()
    params_list = [(stock.code, stock.name) for stock in stock_info.itertuples()]
    """处理日常数据的示例函数"""
    with PgDBUtil(**db_conf) as db:
        logger.info(f"获取到数据，{len(params_list)}行")
        db.execute_update("DELETE FROM stock_info_a_code_name")
        sql = "INSERT INTO stock_info_a_code_name (code, name) VALUES (%s, %s)"
        result = db.execute_batch(sql, params_list)
        logger.info(f"批量插入完成，影响行数: {result}")

def process_daily_data():
    pages = [1, 2, 3, 4, 5]
    get_individual_fund_flow_data('in',pages)
    get_individual_fund_flow_data('out',pages)
    pass


if __name__ == '__main__':
    pages = [1, 2, 3, 4, 5]
    get_individual_fund_flow_data('in',pages)
    get_individual_fund_flow_data('out',pages)
    print("处理完成")

