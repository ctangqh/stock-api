import re
import json
from conf.Config import FIELDS_INDEX_MAP
import datetime
from datetime import datetime, time
from lunarcalendar import Converter  
import pytz
import logging

logger = logging.getLogger(__name__)

class ToolsUtil:
    def __init__(self):
        pass

    @staticmethod
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

    @staticmethod
    def extract_json_from_callback(callback_str):
        """
        从 jQuery 回调函数中提取 JSON 数据
        
        参数:
        callback_str -- jQuery 回调函数字符串，格式为 "jQuery11230919858424235644_1770456637056(json);"
        
        返回:
        提取的 JSON 数据（已转换为 Python 字典）
        """
        # 提取文本内容
        text = ToolsUtil.extract_jquery_callback(callback_str)
        
        if text:
            try:
                # 将 JSON 字符串转换为 Python 字典
                return json.loads(text)
            except json.JSONDecodeError:
                # 如果不是有效的 JSON，返回原始文本
                return text
        else:
            return None

    from urllib.parse import urlparse, parse_qs

    def extract_url_context(url):
        """
        从 URL 中提取上下文请求路径
        
        参数:
        url -- 完整的 URL
        
        返回:
        包含上下文信息的字典，包括基础 URL、路径和查询参数
        """
        # 解析 URL
        parsed_url = urlparse(url)
        
        # 提取基础信息
        context = {
            'scheme': parsed_url.scheme,  # 协议 (http/https)
            'netloc': parsed_url.netloc,  # 网络位置 (域名:端口)
            'path': parsed_url.path,      # 路径
            'params': parsed_url.params,   # 参数
            'query': parsed_url.query,    # 查询字符串
            'fragment': parsed_url.fragment  # 片段
        }
        
        # 构建基础 URL
        base_url = f"{context['scheme']}://{context['netloc']}"
        context['base_url'] = base_url
        
        # 解析查询参数
        query_params = parse_qs(parsed_url.query)
        context['query_params'] = query_params
        
        # 将参数值从列表转换为单个值
        params = {}
        for key, value in query_params.items():
            # 如果参数只有一个值，则直接使用该值
            if len(value) == 1:
                params[key] = value[0]
            # 如果参数有多个值，则保留为列表
            else:
                params[key] = value
        
        context['params'] = params
        
        return context

    @staticmethod
    def json_name_map(json_data, name_map):
        """
        根据名称映射将 JSON 数据中的字段名进行替换

        参数:
        json_data -- JSON 数据（Python 字典）
        name_map -- 名称映射字典，键为原始字段名，值为替换后的字段名

        返回:
        替换字段名后的 JSON 数据（Python 字典）
        """
        data = {}
        for key, value in json_data.items():
            if key in name_map.keys():
                data[name_map[key]] = json_data.get(key)
            else:
                data[key] = value
        return data
    
    @staticmethod
    def fields_data_map(data, fields_map):
        data_list = []
        for item in data:
            temp = ToolsUtil.json_name_map(item, fields_map)
            data_list.append(temp)
        return data_list

    @staticmethod
    def ticker_data_map(data):
        """
        根据名称映射将 DFCF 数据中的字段名进行替换

        参数:
        data -- DFCF 数据（Python 字典）

        返回:
        替换字段名后的 DFCF 数据（Python 字典）
        f12: DJIA (Ticker symbol)
        f14: 道琼斯 (Chinese name for Dow Jones)
        f124: 1770670789 (Timestamp - UNaIX time, which converts to 2025-02-11)
        f13: 100 (Market identifier code)
        Price Data:

        f2: 5,013,587 (Current price/value)
        f17: 5,004,779 (Opening price)
        f18: 5,011,567 (Previous close price)
        f28: 5,011,567 (Likely yesterday's close)
        f15: 5,021,940 (Today's high)
        f16: 4,983,745 (Today's low)
        Change Information:

        f4: 2,020 (Points change - likely from previous close)
        f3: 4 (Change percentage × 100, so 0.04%)
        Other Indicators:

        f1: 2 (Unknown status code)
        f7: 76 (Volume or related metric)
        f152: 2 (Trading status code)
        f292: 5 (Unknown code)
        """
        index_data_list = []
        for item in data:
            temp = ToolsUtil.json_name_map(item, FIELDS_INDEX_MAP)
            index_data_list.append(temp)
        return index_data_list

    @staticmethod
    def is_cn_stock_trading_time():
        """判断当前是否是A股交易时间，返回 (是否交易时间, 缓存时间秒数)"""
        now = datetime.now()
        default_ttl = 60 * 60 * 24
        
        # 周末或节假日直接返回
        if now.weekday() >= 5 or ToolsUtil.is_public_holiday(now):
            return False, default_ttl
        
        current_time = now.time()
        # 交易时间段定义
        morning_start, morning_end = time(9, 30), time(11, 30)
        afternoon_start, afternoon_end = time(13, 0), time(15, 0)
        
        # 收盘后
        if current_time > afternoon_end:
            return False, default_ttl
        
        # 上午交易时间
        if morning_start <= current_time <= morning_end:
            end_dt = datetime.combine(now.date(), morning_end)
            return True, max(1, int((end_dt - now).total_seconds()))
        
        # 下午交易时间
        if afternoon_start <= current_time <= afternoon_end:
            end_dt = datetime.combine(now.date(), afternoon_end)
            return True, max(1, int((end_dt - now).total_seconds()))
        
        # 午间休市
        if morning_end < current_time < afternoon_start:
            start_dt = datetime.combine(now.date(), afternoon_start)
            return False, max(1, int((start_dt - now).total_seconds()))

        # 盘前
        return False, default_ttl

    @staticmethod
    def is_public_holiday(date):
        """判断是否是法定节假日"""
        year = date.year
        month = date.month
        day = date.day
        
        # 元旦节（1月1日）
        if month == 1 and day == 1:
            return True
        
        # 劳动节（5月1日）
        if month == 5 and day == 1:
            return True
        
        # 国庆节（10月1日-7日）
        if month == 10 and 1 <= day <= 7:
            return True
        
        # 清明节（4月4日-6日）
        if month == 4 and 4 <= day <= 6:
            return True
        
        # 农历节日判断
        try:
            lunar = ConverterSolar2Lunar(year, month, day)
            
            # 春节（正月初一到初七）
            if lunar.month == 1 and 1 <= lunar.day <= 7:
                return True
                
            # 端午节（五月初五）
            if lunar.month == 5 and lunar.day == 5:
                return True
                
            # 中秋节（八月十五）
            if lunar.month == 8 and lunar.day == 15:
                return True
                
        except:
            pass
        
        return False

    class ConverterSolar2Lunar:
        """阳历转农历的辅助类"""
        def __init__(self, year, month, day):
            lunar = Converter.solar2lunar(year, month, day)
            self.month = lunar[1]
            self.day = lunar[2]

    @staticmethod
    def is_us_stock_trading_time(include_pre_market=False, include_after_hours=False):
        """
        判断当前是否是美股交易时间
        
        Args:
            include_pre_market: 是否包含盘前交易时间
            include_after_hours: 是否包含盘后交易时间
        
        Returns:
            bool: True表示当前是交易时间，False表示不是交易时间
        """
        # 获取美东时间
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        
        # 检查是否是工作日（周一到周五）
        if now.weekday() >= 5:  # 5代表周六，6代表周日
            return False
        
        # 获取当前时间
        current_time = now.time()
        
        # 正常交易时间：9:30 AM - 4:00 PM
        regular_start = time(9, 30)
        regular_end = time(16, 0)
        
        # 盘前交易时间：4:00 AM - 9:30 AM
        pre_market_start = time(4, 0)
        pre_market_end = time(9, 30)
        
        # 盘后交易时间：4:00 PM - 8:00 PM
        after_hours_start = time(16, 0)
        after_hours_end = time(20, 0)
        
        # 判断是否在交易时间段内
        in_regular_time = regular_start <= current_time <= regular_end
        in_pre_market = include_pre_market and (pre_market_start <= current_time <= pre_market_end)
        in_after_hours = include_after_hours and (after_hours_start <= current_time <= after_hours_end)
        
        return in_regular_time or in_pre_market or in_after_hours
    @staticmethod
    def get_us_market_status():
        """
        获取当前美股市场状态
        
        Returns:
            str: 市场状态描述
        """
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        current_time = now.time()
        
        if now.weekday() >= 5:
            return "周末休市"
        
        if time(4, 0) <= current_time < time(9, 30):
            return "盘前交易"
        elif time(9, 30) <= current_time < time(16, 0):
            return "正常交易"
        elif time(16, 0) <= current_time < time(20, 0):
            return "盘后交易"
        else:
            return "休市"

    @staticmethod
    def merge_dicts(origins_dict: dict, merge_dicts: dict):
        """
        合并两个字典，当键相同时使用dict2的值覆盖dict1的值
        
        Args:
            origins_dict: 原始字典
            merge_dicts: 合并字典
        
        Returns:
            合并后的新字典
        """
        # 创建dict1的副本，避免修改原字典
        result = origins_dict.copy()
        # 使用dict2的值更新结果字典
        result.update(merge_dicts)
        return result

if __name__ == "__main__":
    json_data = '{"f1":2,"f2":5013587,"f3":4,"f4":2020,"f7":76,"f12":"DJIA","f13":100,"f14":"道琼斯","f15":5021940,"f16":4983745,"f17":5004779,"f18":5011567,"f28":5011567,"f124":1770670789,"f152":2,"f292":5}'
    data =  json.loads(json_data)
    name_map = {
        "f1": "交易状态(2:正常交易,0:已收盘)",
        "f2": "当前指数",
        "f3": "涨跌幅(%)",
        "f4": "涨跌幅(点)",
        "f6": "成交额(元)",
        "f6_bn": "成交额(亿元)",
        "f7": "成交量(手)",
        "f12": "指数代码",
        "f13": "市场标识(1:A股,100:美股)",
        "f14": "指数名称",
        "f15": "今日最高",
        "f16": "今日最低",
        "f17": "开盘价",
        "f18": "前收盘价",
        "f28": "昨日收盘价",
        "f106": "委比(%)",
        "f104": "外盘",
        "f105": "内盘",
        "f124": "更新时间戳(UNIX时间)",
        "f152": "交易状态(2:正常交易,0:已收盘)",
        "f292": "未知代码"
    }
    ### 国内市场信息
# | 字段 | 数据类型 | 示例值 | 对应含义 |
# | :--- | :--- | :--- | :--- |
# | **f1** | SMALLINT | 2 | 状态码 (2:正常交易, 0:已收盘) |
# | **f2** | DECIMAL(10, 2) | 4128.93 | 当前指数值 |
# | **f3** | DECIMAL(5, 2) | 0.14 | 涨跌幅 (%) |
# | **f4** | DECIMAL(7, 2) | 5.84 | 涨跌额 (点) |
# | **f6** | DECIMAL(18, 1) | 647985947582.7 | 成交额 (元) |
# | **f6_bn** | DECIMAL(8, 2) | 6479.86 | 成交额 (亿元) |
# | **f12** | VARCHAR(10) | 000001 | 上证指数代码 |
# | **f13** | SMALLINT | 1 | 市场标识 (代表上海证券交易所) |
# | **f104** | INT | 1031 | 外盘 |
# | **f105** | INT | 1219 | 内盘 |
# ### 美股市场信息
# | 字段 | 数据类型 | 示例值 | 对应含义 |
# | :--- | :--- | :--- | :--- |
# | **f1** | SMALLINT | 2 | 未知状态码 |
# | **f2** | BIGINT | 5013587 | 当前指数值 |
# | **f3** | DECIMAL(5, 2) | 4 | 涨跌幅 × 100 (即 0.04%) |
# | **f4** | BIGINT | 2020 | 涨跌点数 (可能相对前收盘价) |
# | **f7** | SMALLINT | 76 | 成交量或相关指标 |
# | **f12** | VARCHAR(10) | DJIA | 股票/指数代码 |
# | **f13** | SMALLINT | 100 | 市场标识码 (代表美股) |
# | **f14** | VARCHAR(50) | 道琼斯 | 股票/指数中文名称 |
# | **f15** | BIGINT | 5021940 | 今日最高价 |
# | **f16** | BIGINT | 4983745 | 今日最低价 |
# | **f17** | BIGINT | 5004779 | 开盘价 |
# | **f18** | BIGINT | 5011567 | 前收盘价 |
# | **f28** | BIGINT | 5011567 | 可能为昨日收盘价 |
# | **f106** | SMALLINT | 95 | 委比或相关比率 (为95%) |
# | **f124** | BIGINT | 1770670789 | 更新时间戳 (UNIX时间) |
# | **f152** | SMALLINT | 2 | 交易状态码 |
# | **f292** | SMALLINT | 5 | 未知代码 |
    stock_data = '[{"f1":2,"f2":4128.93,"f3":0.14,"f4":5.84,"f6":647985947582.7,"f12":"000001","f13":1,"f104":1031,"f105":1219,"f106":95,"f6_bn":6479.86},{"f1":2,"f2":14222.91,"f3":0.1,"f4":14.47,"f6":905274339912.8384,"f12":"399001","f13":0,"f104":1476,"f105":1332,"f106":104,"f6_bn":9052.74},{"f1":2,"f2":2323867,"f3":90,"f4":20746,"f7":189,"f12":"NDX","f13":100,"f14":"纳斯达克","f15":2331467,"f16":2287837,"f17":2295224,"f18":2303121,"f28":2303121,"f124":1770670800,"f152":2,"f292":5},{"f1":2,"f2":696482,"f3":47,"f4":3252,"f7":107,"f12":"SPX","f13":100,"f14":"标普500","f15":698010,"f16":690587,"f17":691726,"f18":693230,"f28":693230,"f124":1770670783,"f152":2,"f292":5},{"f1":2,"f2":5013587,"f3":4,"f4":2020,"f7":76,"f12":"DJIA","f13":100,"f14":"道琼斯","f15":5021940,"f16":4983745,"f17":5004779,"f18":5011567,"f28":5011567,"f124":1770670789,"f152":2,"f292":5}]'
    data =  json.loads(stock_data)
    t = ToolsUtil()
    s = ToolsUtil.ticker_data_map(data)
    print(s)

    if is_a_stock_trading_time():
        print("当前是A股交易时间")
    else:
        print("当前不是A股交易时间")
