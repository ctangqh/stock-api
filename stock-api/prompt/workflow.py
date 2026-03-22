import json
import logging

logger = logging.getLogger(__name__)

def main(jdata: str) -> dict:
    try:
        logger.info("开始处理提示工作流")
        # 1. 解析输入数据 (假设传入的是字符串格式的 JSON)
        # 如果前序节点直接传的是 Object，这里可能不需要 json.loads，视 Dify 版本而定
        # 为了稳健，先判断类型
        if isinstance(jdata, str):
            data = json.loads(jdata)
        else:
            data = jdata
            
        # 2. 定义我们需要关注的核心指数 (过滤掉 B 股、综合指数等噪音)
        # 键是 API 里的 '名称'，值是我们想展示的显示名称（如果一样可不改）
        target_indices = {
            "000001": "上证指数",
            "399001": "深证成指",
        }

        # 3. 初始化变量
        summary_lines = []
        total_turnover = 0.0
        up_count = 0
        down_count = 0
        mid_count = 0
        
        # 4. 遍历数据并提取信息
        # API 返回的是一个列表，我们需要找到对应名字的项
        found_data = {}
        for item in data:
            total_turnover += float(data.get('f16'))
            up_count += float(data.get('f104'))
            down_count += float(data.get('f105'))
            mid_count += float(data.get('f106'))
            
        # 5. 按照我们定义的顺序生成格式化文本
        output_text = "### 🇨🇳 A股大盘核心数据\n"
        
        for item in data:
            display_name = target_indices.get(item.get("f12", '000001'))
            pct_change = float(item.get("f14", 0))
            price = item.get("f2", 0)
            if pct_change > 0:
                icon = "🔴" 
            elif pct_change < 0:
                icon = "🟢"
            else:
                icon = "⚪"   
            # 格式化单行: - 🔴 **上证指数**: 1.25% (现价: 3200.5)
            line = f"- {icon} **{display_name}**: {pct_change}% (现价: {price})"
            summary_lines.append(line)         

        # 6. 添加成交额数据 (转换为亿元)
        turnover_billion = total_turnover / 100000000
        summary_lines.append(f"\n💰 **两市成交额**: {turnover_billion:.0f}亿")
        
        # 7. 简单的市场情绪总结（给大模型的一句话Context）
        sentiment = "市场情绪偏暖" if up_count > down_count else "市场情绪偏弱"
        if abs(up_count - down_count) <= 1: sentiment = "市场分化震荡"
        summary_lines.append(f"📈 **整体概况**: {sentiment} (个股有 {up_count}涨，{down_count}跌)")

        # 拼接最终文本
        final_string = output_text + "\n".join(summary_lines)
        
        return {
            "result": final_string
        }

    except Exception as e:
        return {
            "result": f"数据处理出错: {str(e)}"
        }