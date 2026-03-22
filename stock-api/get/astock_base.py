from util.ToolsUtil import ToolsUtil
from util.HttpUtil import HttpUtil
from data.stock_real import StockDataParser
from conf.Config import CLIENT_SET, CLIENT_SET2
import json, logging
# 获取大盘数据
# https://push2.eastmoney.com/api/qt/ulist.np/get?cb=jQuery11230806474628323575_1770647354626&fltt=2&secids=1.000001%2C0.399001&fields=f1%2Cf2%2Cf3%2Cf4%2Cf6%2Cf12%2Cf13%2Cf104%2Cf105%2Cf106&ut=b2884a393a59ad64002292a3e90d46a5&_=1770647354627

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_astock_price(symbol: str):
    url = f"http://qt.gtimg.cn/q={symbol}"
    print(url)
    base_url, context, params = HttpUtil.get_request_url_info(url)
    default_headers = CLIENT_SET2.get('headers')
    http_util = HttpUtil(base_url, default_headers, None, 30)
    with http_util:
        try:
        # 发送 GET 请求
            response = http_util.get(context, params=params)
            logger.info(f"请求到股票报价数据: {response.content}")
            price = StockDataParser(response.text).get_summary()["基本信息"]
            return price
        except Exception as e:
            logger.error(f"处理失败: {str(e)}")
            return {"error": f"处理失败: {str(e)}"}, 500

def get_astock_index():
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get?cb=jQuery11230806474628323575_1770647354626&fltt=2&secids=1.000001%2C0.399001&fields=f1%2Cf2%2Cf3%2Cf4%2Cf6%2Cf12%2Cf13%2Cf104%2Cf105%2Cf106&ut=b2884a393a59ad64002292a3e90d46a5&_=1770647354627"
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
        "Referer": "https://data.eastmoney.com/zjlx/dpzjlx.html"
    }
    default_headers = CLIENT_SET.get('headers')
    default_headers["Referer"] = "https://data.eastmoney.com/zjlx/dpzjlx.html"
    cookie_str = CLIENT_SET.get('cookie')
    default_cookies= HttpUtil.cookie_translate(cookie_str)
    http_util = HttpUtil(base_url, default_headers, default_cookies, 30)
    fund_flow_list = []
    data = None
    with http_util:
        try:
        # 发送 GET 请求
            logger.debug(f"请求参数: {params}")
            response = http_util.get(HttpUtil.url_context(url).get('path'), params=params)
            data = ToolsUtil.extract_json_from_callback(response.text)['data']['diff']
            logger.info(f"从远程URL请求完成，状态码: {response.status_code}")
        except Exception as e:
            logger.exception(f"GET 请求异常: {e}")
    return data

def get_usstock_index():
    url = "https://push2.eastmoney.com/api/qt/clist/get?np=1&fltt=1&invt=2&cb=jQuery371014817924919844483_1770685816533&fs=i%3A100.NDX%2Ci%3A100.DJIA%2Ci%3A100.SPX&fields=f12%2Cf13%2Cf14%2Cf292%2Cf1%2Cf2%2Cf4%2Cf3%2Cf152%2Cf17%2Cf28%2Cf15%2Cf16%2Cf18%2Cf7%2Cf124&fid=f3&pn=1&pz=20&po=1&dect=1&ut=b2884a393a59ad64002292a3e90d46a5&wbp2u=%7C0%7C0%7C0%7Cweb&_=1770685816538"
    base_url, params = HttpUtil.url2param(url)
    default_headers = CLIENT_SET.get('headers')
    default_headers["Referer"] = "https://data.eastmoney.com/center/grid.html#hs_a_board"
    cookie_str = CLIENT_SET.get('cookie')
    default_cookies= HttpUtil.cookie_translate(cookie_str)
    http_util = HttpUtil(base_url, default_headers, default_cookies, 30)
    fund_flow_list = []
    data = None
    with http_util:
        try:
        # 发送 GET 请求
            response = http_util.get(HttpUtil.url_context(url).get('path'), params=params)
            data = ToolsUtil.extract_json_from_callback(response.text)['data']['diff']
            print(f"从远程URL请求: {response.status_code}")
        except Exception as e:
            print(f"GET 请求异常: {e}")
    return data
# 大盤資金流向數據
# https://quote.eastmoney.com/center/hszs.html
# https://push2.eastmoney.com/api/qt/ulist.np/get?cb=jQuery11230841890186182231_1770738118847&fltt=2&secids=1.000001%2C0.399001&fields=f62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf64%2Cf65%2Cf70%2Cf71%2Cf76%2Cf77%2Cf82%2Cf83%2Cf164%2Cf166%2Cf168%2Cf170%2Cf172%2Cf252%2Cf253%2Cf254%2Cf255%2Cf256%2Cf124%2Cf6%2Cf278%2Cf279%2Cf280%2Cf281%2Cf282&ut=b2884a393a59ad64002292a3e90d46a5&_=1770738118848
# 
def get_cnstock_funds_flow():
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get?cb=jQuery11230841890186182231_1770738118847&fltt=2&secids=1.000001%2C0.399001&fields=f62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf64%2Cf65%2Cf70%2Cf71%2Cf76%2Cf77%2Cf82%2Cf83%2Cf164%2Cf166%2Cf168%2Cf170%2Cf172%2Cf252%2Cf253%2Cf254%2Cf255%2Cf256%2Cf124%2Cf6%2Cf278%2Cf279%2Cf280%2Cf281%2Cf282&ut=b2884a393a59ad64002292a3e90d46a5&_=1770738118848"
    base_url, params = HttpUtil.url2param(url)
    default_headers = CLIENT_SET.get('headers')["Referer"] = "https://data.eastmoney.com/zjlx/dpzjlx.html"
    cookie_str = CLIENT_SET.get('cookie')
    #cookie_str = "qgqp_b_id=476adfb9b95b9c52be2a02dbc2fe5005; st_nvi=ZaT6vtQIJcsU1WERopjqY0258; nid18=0c761ad2ddf5902ad2bb97b3d8031392; nid18_create_time=1768136306577; gviem=IaR46LxELHLsqxDEao4hY0821; gviem_create_time=1768136306578; fullscreengg=1; fullscreengg2=1; st_si=56798892871416; st_asi=delete; st_pvi=96913291039558; st_sp=2026-01-11%2020%3A58%3A23; st_inirUrl=https%3A%2F%2Fwww.google.com.hk%2F; st_sn=51; st_psi=20260209222853733-113300300871-6141524522"
    default_cookies= HttpUtil.cookie_translate(cookie_str)
    http_util = HttpUtil(base_url, default_headers, default_cookies, 30)
    fund_flow_list = []
    data = None
    with http_util:
        try:
            response = http_util.get(HttpUtil.url_context(url).get('path'), params=params)
            data = ToolsUtil.extract_json_from_callback(response.text)['data']['diff']
            print(f"从远程URL请求: {response.status_code}")
        except Exception as e:
            print(f"GET 请求异常: {e}")
    return data

def get_cnstock_trade_summary():
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get?cb=jQuery11230841890186182231_1770738118842&fltt=2&secids=1.000001%2C0.399001&fields=f1%2Cf2%2Cf3%2Cf4%2Cf6%2Cf12%2Cf13%2Cf104%2Cf105%2Cf106&ut=b2884a393a59ad64002292a3e90d46a5&_=1770738118844"
    base_url, params = HttpUtil.url2param(url)
    default_headers = CLIENT_SET.get('headers')
    default_headers["Referer"] = "https://data.eastmoney.com/zjlx/dpzjlx.html"
    cookie_str = CLIENT_SET.get('cookie')
    default_cookies= HttpUtil.cookie_translate(cookie_str)
    http_util = HttpUtil(base_url, default_headers, default_cookies, 30)
    fund_flow_list = []
    data = None
    with http_util:
        try:
        # 发送 GET 请求
            logger.debug(f"请求参数: {params}")
            response = http_util.get(HttpUtil.url_context(url).get('path'), params=params)
            data = ToolsUtil.extract_json_from_callback(response.text)['data']['diff']
            logger.info(f"从远程URL请求完成，状态码: {response.status_code}")
        except Exception as e:
            logger.exception(f"GET 请求异常: {e}")
    return data

def cn_stock_gg_fund_flow():
    url = "https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery1123011793120366460874_1771996414177&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13"
    http_util,params = build_http(url,{"Referer":"https://data.eastmoney.com/zjlx/dpzjlx.html"})
    with http_util:
        try:
            # 发送 GET 请求
            response = http_util.get(HttpUtil.url_context(url).get('path'), params=params)
            data = ToolsUtil.extract_json_from_callback(response.text)['data']['diff']
            print(data)
            print(f"从远程URL请求: {response.status_code}")
        except Exception as e:
            print(f"GET 请求异常: {e}")
    pass

def cn_stock_bk_fund_flow():
    url_hy = "https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112308398943146220799_1770870961085&fid=f62&po=1&pz=10&pn=1&np=1&fltt=2&invt=2&fs=m%3A90+t%3A2&stat=1&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124&ut=8dec03ba335b81bf4ebdf7b29ec27d15"
    url_gn = "https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112308398943146220799_1770870961086&fid=f62&po=1&pz=10&pn=1&np=1&fltt=2&invt=2&fs=m%3A90+t%3A3&stat=1&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124&ut=8dec03ba335b81bf4ebdf7b29ec27d15"
    url_dy = "https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112308398943146220799_1770870961087&fid=f62&po=1&pz=10&pn=1&np=1&fltt=2&invt=2&fs=m%3A90+t%3A1&stat=1&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124&ut=8dec03ba335b81bf4ebdf7b29ec27d15"
    http_util,params = build_http(url_hy,{"Referer":"https://data.eastmoney.com/bkzj/"})
    bk_fund_flows = {}
    reqs_urls = {"行业板块":url_hy, "概念板块": url_gn, "地域板块":url_dy}
    data = None
    with http_util:
        for key in reqs_urls.keys():
            url = reqs_urls.get(key)
            try:
                # 发送 GET 请求
                _, params = build_http(url,{"Referer":"https://data.eastmoney.com/bkzj/"})
                response = http_util.get(HttpUtil.url_context(url).get('path'), params=params)
                data = ToolsUtil.extract_json_from_callback(response.text)['data']['diff']
                print(f"从远程URL请求: {response.status_code}")
            except Exception as e:
                print(f"GET 请求异常: {e}")
            bk_fund_flows[key] = data
    return bk_fund_flows


def build_http(url: str, headers_dict: dict = {}, params_dict: dict = {}):
    base_url, params = HttpUtil.url2param(url)
    default_headers = CLIENT_SET.get('headers')
    default_headers = ToolsUtil.merge_dicts(default_headers, headers_dict)
    params_dict.update({"ut": CLIENT_SET.get('ut')})
    params = ToolsUtil.merge_dicts(params, params_dict)
    cookie_str = CLIENT_SET.get('cookie')
    default_cookies= HttpUtil.cookie_translate(cookie_str)
    http_util = HttpUtil(base_url, default_headers, default_cookies, 30)
    return http_util,params

def stock_index2str(data, brief=False):
    """
    将股票指数数据转换为中文总结语句
    
    参数:
        data: 包含指数数据的字典列表或JSON字符串
        brief: 是否返回简洁版本
        
    返回:
        str: 总结语句
    """
    # 确保data是列表格式
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            return "数据格式错误"
    
    # 通过f12识别上证指数和深证成指
    shanghai_data = None
    shenzhen_data = None
    
    for item in data:
        if item.get("f12") == "000001":  # 上证指数代码
            shanghai_data = item
        elif item.get("f12") == "399001":  # 深证成指代码
            shenzhen_data = item
    
    # 检查是否找到两个指数的数据
    if shanghai_data is None or shenzhen_data is None:
        return "数据不完整，缺少上证指数或深证成指数据"
    
    # 将成交额转换为亿元
    shanghai_data["f6_bn"] = round(shanghai_data["f6"] / 100000000, 2)
    shenzhen_data["f6_bn"] = round(shenzhen_data["f6"] / 100000000, 2)
    
    # 函数：判断涨跌并返回相应符号和描述
    def get_change_info(f3, f4):
        if f3 > 0:
            return f"+{f3}%", "上涨", f"+{f4}"
        elif f3 < 0:
            return f"{f3}%", "下跌", f"{f4}"
        else:
            return "0%", "平盘", "0"
    
    # 获取各指数涨跌信息
    shanghai_change = get_change_info(shanghai_data["f3"], shanghai_data["f4"])
    shenzhen_change = get_change_info(shenzhen_data["f3"], shenzhen_data["f4"])
    
    # 计算两市总数据
    total_volume = shanghai_data["f6_bn"] + shenzhen_data["f6_bn"]
    total_up = shanghai_data["f104"] + shenzhen_data["f104"]
    total_down = shanghai_data["f105"] + shenzhen_data["f105"]
    
    # 判断市场整体情绪
    market_status = "普涨" if total_up > total_down * 1.5 else (
        "普跌" if total_down > total_up * 1.5 else "分化"
    )
    
    # 判断涨跌符号
    sh_symbol = "+" if shanghai_data["f3"] > 0 else ("-" if shanghai_data["f3"] < 0 else "")
    sz_symbol = "+" if shenzhen_data["f3"] > 0 else ("-" if shenzhen_data["f3"] < 0 else "")
    
    if brief:
        # 简洁版本
        summary = f"收盘：沪指{sh_symbol}{abs(shanghai_data['f3'])}%收{shanghai_data['f2']}点，深指{sz_symbol}{abs(shenzhen_data['f3'])}%收{shenzhen_data['f2']}点，成交{total_volume:.0f}亿，{total_up}股涨，{total_down}股跌。"
    else:
        # 详细版本
        summary = f"收盘简评：上证指数{shanghai_data['f2']}点（{shanghai_change[0]}），{shanghai_change[1]} {shanghai_data['f4']}点；深证成指{shenzhen_data['f2']}点（{shenzhen_change[0]}），{shenzhen_change[1]} {shenzhen_data['f4']}点。两市成交额{total_volume:.0f}亿元，上涨个股{total_up}只，下跌个股{total_down}只，市场呈现{market_status}格局。"
    
    return summary

