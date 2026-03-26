import os

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '192.168.3.3'),
    'port': int(os.environ.get('DB_PORT', '5433')),
    'database': os.environ.get('DB_NAME', 'stock'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres')
}

# Redis 配置
REDIS_CONFIG = {
    'host': os.environ.get('REDIS_HOST', '192.168.3.3'),
    'port': int(os.environ.get('REDIS_PORT', '6379')),
    'db': int(os.environ.get('REDIS_DB', '0')),
    'password': os.environ.get('REDIS_PASSWORD', None),
    'decode_responses': True,
    'socket_timeout': 5,
    'socket_connect_timeout': 5
}

# 請求客戶端設置
CLIENT_SET = {
    "cookie": "qgqp_b_id=476adfb9b95b9c52be2a02dbc2fe5005; st_nvi=ZaT6vtQIJcsU1WERopjqY0258; nid18=0c761ad2ddf5902ad2bb97b3d8031392; nid18_create_time=1768136306577; gviem=IaR46LxELHLsqxDEao4hY0821; gviem_create_time=1768136306578; fullscreengg=1; fullscreengg2=1; st_si=56798892871416; websitepoptg_api_time=1770455742795; st_asi=delete; st_pvi=96913291039558; st_sp=2026-01-11%2020%3A58%3A23; st_inirUrl=https%3A%2F%2Fwww.google.com.hk%2F; st_sn=15; st_psi=20260207173021173-113200313000-8368862338",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Content-Type": "application/javascriyypt; charset=UTF-8",
        "Host": "push2.eastmoney.com",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest":"script",
        "Sec-Fetch-Mode":"no-cors", 
        "Sec-Fetch-Site":"same-site",
        "Sec-Ch-Ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "Referer": "https://data.eastmoney.com/zjlx/dpzjlx.html"
    },
    "ut": "b2884a393a59ad64002292a3e90d46a5"
}

CLIENT_SET2 = {
    "headers": {
        "Accept-language":"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Host": "qt.gtimg.cn",
        "Cache-Control": "max-age=0",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection":"keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
}

# 指數列表
FIELDS_INDEX_MAP = {
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

# f6	882,201,747,043.8	当日总成交额（约8822亿元）
# f62	-16,013,291,520.0	主力净流入（大单）（-160.1亿元）
# f64	129,276,944,384.0	大单买入额
# f65	137,113,350,144.0	大单卖出额
# f66	-7,836,405,760.0	大单净流入（-78.4亿元）
# f69	-0.89	大单净流入率（-0.89%）
# f70	224,733,786,112.0	中单买入额
# f71	232,910,671,872.0	中单卖出额
# f72	-8,176,885,760.0	中单净流入（-81.8亿元）
# f75	-0.93	中单净流入率（-0.93%）
# f76	276,386,197,504.0	小单买入额
# f77	274,479,820,800.0	小单卖出额
# f78	1,906,376,704.0	小单净流入（+19.1亿元）
# f81	0.22	小单净流入率（+0.22%）
# f82	234,985,242,624.0	散户买入额（或“其他”类别）
# f83	220,878,323,712.0	散户卖出额
# f84	14,106,918,912.0	散户净流入（+141.1亿元）
# f87	1.6	散户净流入率（+1.60%）
# f124	1,770,711,105	参与交易的账户数（或“成交笔数”）
# f164	-58,213,646,336.0	今日主力净流入（-582.1亿元）
# f166	-22,520,463,360.0	今日超大单净流入（-225.2亿元）
# f168	-35,693,182,976.0	今日大单净流入（-356.9亿元）
# f170	-2,719,600,640.0	今日中单净流入（-27.2亿元）
# f172	60,933,242,880.0	今日小单净流入（+609.3亿元）
# f184	-1.82	主力净流入率（-1.82%）
# f252	-427,422,642,176.0	今日北向资金净流入（-4274.2亿元？需注意单位可能与实际不符，通常北向资金规模没这么大，可能是所有外资统计）
# f253	-259,155,591,168.0	今日南向资金净流入（-2591.6亿元？同样单位可能为“万元”或接口放大倍数）
# f254	-168,267,051,008.0	今日融资净买入（-1682.7亿元？）
# f255	82,756,284,416.0	今日融券净卖出（+827.6亿元？）
# f256	344,666,353,664.0	今日融资融券净差额（+3446.7亿元？）
# f278 ~ f282	与 f164 ~ f172 部分重复	可能是不同时间维度（如“当日累计” vs “实时”）的同类资金流数据
# f1	2	可能表示状态码（如“交易中”）
# f2	14210.63	最新价/当前指数点位（深圳成指今日收盘价为 14210.63？）
# f3	0.02	涨跌幅（+0.02%，今日微涨）
# f4	2.19	上涨数值（较前一交易日上涨 2.19 点）
# f6	1223333554475.6643	成交额（单位可能是元，约 1.22 万亿元）
# f12	"399001"	代码（深圳成指指数代码）
# f13	0	市场类型（0 可能表示深市）
# f104	1257	上涨家数
# f105	1562	下跌家数
# f106	93	平盘家数
FIELDS_FUNDS_FLOW_MAP = {
    "f1": "交易状态(2:正常交易,0:已收盘)",
    "f2": "当前指数",
    "f3": "涨跌幅(%)",
    "f4": "涨跌幅(点)",
    "f6": "当日总成交额(亿元)",
    "f12": "指数代码",
    "f13": "市场标识(0:深指,1:上指)",
    "f62": "主力净流入(亿元)",
    "f64": "大单买入额(亿元)",
    "f65": "大单卖出额(亿元)",
    "f66": "大单净流入(亿元)",
    "f69": "大单净流入率(%)",
    "f70": "中单买入额(亿元)",
    "f71": "中单卖出额(亿元)",
    "f72": "中单净流入(亿元)",
    "f75": "中单净流入率(%)",
    "f76": "小单买入额(亿元)",
    "f77": "小单卖出额(亿元)",
    "f78": "小单净流入(亿元)",
    "f81": "小单净流入率(%)",
    "f82": "散户买入额(亿元)",
    "f83": "散户卖出额(亿元)",
    "f84": "散户净流入(亿元)",
    "f87": "散户净流入率(%)",
    "f104": "上涨家数",
    "f105": "下跌家数",
    "f106": "平盘家数",
    "f124": "成交笔数",
    "f164": "今日主力净流入(亿元)",
    "f166": "今日超大单净流入(亿元)",
    "f168": "今日大单净流入(亿元)",
    "f170": "今日中单净流入(亿元)",
    "f172": "今日小单净流入(亿元)",
    "f184": "今日主力净流入率(%)",
    "f252": "今日北向资金净流入(亿元)",
    "f253": "今日南向资金净流入(亿元)",
    "f254": "今日融资净买入(亿元)",
    "f255": "今日融券净卖出(亿元)",
    "f256": "今日融资融券净差额(亿元)" 
}

# 定时任务配置
SCHEDULER_CONFIG = {
    # 选股任务定时配置
    'stock_scan': {
        'enabled': os.environ.get('SCHEDULER_STOCK_SCAN_ENABLED', 'true').lower() == 'true',
        # Cron 表达式: 分 时 日 月 周
        # 每天晚上 8:30 执行: '30 20 * * *'
        'cron': os.environ.get('SCHEDULER_STOCK_SCAN_CRON', '30 20 * * *')
    }
}

# 技术指标配置
def _parse_list_env(env_value, default):
    """解析逗号分隔的环境变量为列表"""
    value = os.environ.get(env_value)
    if value:
        return [int(x.strip()) for x in value.split(',') if x.strip()]
    return default

TECHNICAL_CONFIG = {
    # MACD 指标参数
    'MACD_FAST': int(os.environ.get('MACD_FAST', '12')),
    'MACD_SLOW': int(os.environ.get('MACD_SLOW', '26')),
    'MACD_SIGNAL': int(os.environ.get('MACD_SIGNAL', '9')),
    # 均线周期
    'MA_PERIODS': _parse_list_env('MA_PERIODS', [5, 10, 20, 60]),
    # 金叉死叉均线参数
    'GOLDEN_CROSS_MA_SHORT': int(os.environ.get('GOLDEN_CROSS_MA_SHORT', '5')),
    'GOLDEN_CROSS_MA_LONG': int(os.environ.get('GOLDEN_CROSS_MA_LONG', '20')),
    'DEATH_CROSS_MA_SHORT': int(os.environ.get('DEATH_CROSS_MA_SHORT', '5')),
    'DEATH_CROSS_MA_LONG': int(os.environ.get('DEATH_CROSS_MA_LONG', '20')),
    # 看涨信号周期
    'BULLISH_PERIODS': _parse_list_env('BULLISH_PERIODS', [5, 10, 20, 60]),
    # 数据范围参数
    'DEFAULT_LOOKBACK_DAYS': int(os.environ.get('DEFAULT_LOOKBACK_DAYS', '500')),
    'MAX_DATE_RANGE_DAYS': int(os.environ.get('MAX_DATE_RANGE_DAYS', '366'))
}

