class StockDataParser:
    """
    股票数据解析器类
    """
    
    # 字段定义（位置: 字段名）
    FIELD_MAPPING = {
        1: '股票名称',
        2: '股票代码',
        3: '当前价',
        4: '昨收价',
        5: '开盘价',
        6: '成交量(手)',
        7: '外盘',
        8: '内盘',
        30: '时间',
        31: '涨跌价',
        32: '涨幅%',
        37: '成交额(万)',
        38: '换手率%',
        39: '市盈率',
        41: '最高价',
        42: '最低价',
        44: '流通值(亿)',
        45: '总市值(亿)',
        47: '涨停价',
        48: '跌停价',
        49: '量比',
        51: '均价',
        52: '动态市盈',
    }
    
    def __init__(self, data_string):
        self.raw_data = data_string
        self.fields = self._extract_fields()

    def p(self):
        return self.fields

    def _extract_fields(self):
        """提取并分割字段"""
        import re
        match = re.search(r'="([^"]+)";', self.raw_data)
        if not match:
            raise ValueError("Invalid data format")
        return match.group(1).split('~')
    
    def get_basic_info(self):
        """获取基本信息"""
        info = {}
        for pos, name in self.FIELD_MAPPING.items():
            if pos < len(self.fields) and self.fields[pos]:
                try:
                    # 尝试转换为数字
                    if name in ['当前价', '昨收价', '开盘价', '最高价', '最低价', '均价', '涨跌', '涨幅%', '量比']:
                        info[name] = float(self.fields[pos])
                    elif name in ['成交量(手)', '成交额(万)', '外盘', '内盘']:
                        info[name] = int(self.fields[pos])
                    else:
                        info[name] = self.fields[pos]
                except (ValueError, TypeError):
                    info[name] = self.fields[pos]
        return info
    
    def get_quotes(self, quote_type='sell'):
        """
        获取五档报价
        quote_type: 'sell' 卖盘, 'buy' 买盘
        """
        quotes = []
        start_idx = 15 if quote_type == 'sell' else 25
        
        for i in range(5):
            price_idx = start_idx + i*2
            vol_idx = start_idx + 1 + i*2
            
            if (price_idx < len(self.fields) and vol_idx < len(self.fields) and 
                self.fields[price_idx] and self.fields[vol_idx]):
                quotes.append({
                    '价格': float(self.fields[price_idx]),
                    '数量(手)': int(self.fields[vol_idx])
                })
        return quotes
    

    def get_trade_info(self):
        """获取交易信息"""
        if len(self.fields) <= 42:
            return {}
        
        trade_str = self.fields[42]
        if not trade_str or not trade_str.strip():  # 检查是否为空或空白字符串
            return {}
            
        if '/' in trade_str:
            parts = trade_str.split('/')
            try:
                # 安全转换函数
                def safe_float(val):
                    try:
                        cleaned_val = val.strip() if val else ''
                        if not cleaned_val:
                            return None
                        # 移除可能的非数字字符（保留小数点和负号）
                        cleaned_val = ''.join(c for c in cleaned_val if c.isdigit() or c == '.' or c == '-')
                        return float(cleaned_val) if cleaned_val else None
                    except (ValueError, TypeError):
                        return None
                
                def safe_int(val):
                    try:
                        cleaned_val = val.strip() if val else ''
                        if not cleaned_val:
                            return None
                        # 移除可能的非数字字符（保留负号）
                        cleaned_val = ''.join(c for c in cleaned_val if c.isdigit() or c == '-')
                        return int(cleaned_val) if cleaned_val else None
                    except (ValueError, TypeError):
                        return None
                
                result = {
                    '成交价': safe_float(parts[0]) if len(parts) > 0 else None,
                    '成交量(手)': safe_int(parts[1]) if len(parts) > 1 else None,
                    '成交额(元)': float(parts[2]) if len(parts) > 2 and parts[2] and parts[2].strip() else None
                }
                
                # 只有当至少有一个有效值时才返回结果
                if any(v is not None for v in result.values()):
                    return result
                return {}
            except Exception as e:
                print(f"解析交易信息时出错: {e}")
                return {}
        return {}


    
    def get_summary(self):
        """获取完整摘要"""
        return {
            '基本信息': self.get_basic_info(),
            '交易信息': self.get_trade_info(),
            # '卖盘': self.get_quotes('sell'),
            # '买盘': self.get_quotes('buy'),
            '更新时间': self.fields[37] if len(self.fields) > 37 else None
        }

if __name__ == '__main__':
    # 使用示例
    data = 'v_sz002202="51~金风科技~002202~31.43~31.29~31.35~3941956~1968986~1972970~31.43~4809~31.42~24592~31.41~2786~31.40~2739~31.39~341~31.44~474~31.45~1073~31.46~636~31.47~1210~31.48~1141~~20260313161430~0.14~0.45~32.68~31.00~31.43/3941956/12534772376~3941956~1253477~11.72~50.04~~32.68~31.00~5.37~1057.15~1327.54~3.46~34.42~28.16~1.27~30733~31.80~38.53~71.36~~~1.80~1253477.2376~0.0000~0~ ~GP-A~54.07~10.40~0.45~6.46~1.68~37.03~7.50~10.47~26.63~101.60~3363505081~4223788647~77.22~215.56~3363505081~~~253.54~-0.51~~CNY~0~~31.50~-2785~";'

    parser = StockDataParser(data)
    print(parser.p())
    summary = parser.get_summary()
    print(summary)

    print("=== 股票数据解析（面向对象方式）===")
    print("\n【基本信息】")
    for key, value in summary['基本信息'].items():
        print(f"  {key}: {value}")

    print("\n【交易信息】")
    for key, value in summary['交易信息'].items():
        print(f"  {key}: {value}")

    # print("\n【五档盘口】")
    # print("  卖盘:")
    # for i, sell in enumerate(summary['卖盘'], 1):
    #     print(f"    卖{i}: {sell['价格']:>6}元  {sell['数量(手)']:>6}手")
    # print("  买盘:")
    # for i, buy in enumerate(summary['买盘'], 1):
    #     print(f"    买{i}: {buy['价格']:>6}元  {buy['数量(手)']:>6}手")
