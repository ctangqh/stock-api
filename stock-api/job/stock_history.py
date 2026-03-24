import logging
import datetime
import time
import argparse
from typing import Dict, List

from conf.Config import TECHNICAL_CONFIG, DB_CONFIG, REDIS_CONFIG
from get.stock_history import StockHistoryDataFetcher

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sync_single_stock(symbol: str) -> bool:
    """
    同步单只股票的历史数据
    
    参数:
    symbol -- 股票代码
    
    返回:
    bool -- 成功返回 True，失败返回 False
    """
    logger.info(f"开始同步股票历史数据: {symbol}")
    try:
        # 初始化数据获取类
        fetcher = StockHistoryDataFetcher(DB_CONFIG, REDIS_CONFIG)
        
        # 获取股票历史数据
        df = fetcher.fetch_stock_history(symbol)
        if df is None or df.empty:
            logger.warning(f"未获取到股票 {symbol} 的历史数据")
            return False
        
        # 同步到数据库
        success_count = fetcher.sync_to_database(df, symbol)
        logger.info(f"股票 {symbol} 历史数据同步完成，成功: {success_count} 条")
        return True
    except Exception as e:
        logger.exception(f"同步股票 {symbol} 历史数据时发生异常: {e}")
        return False


def sync_all_stocks(limit: int = 100) -> Dict[str, int]:
    """
    批量同步股票历史数据
    
    参数:
    limit -- 限制同步的股票数量，默认 100
    
    返回:
    dict -- 包含成功和失败数量的字典，格式: {'success': count, 'failed': count}
    """
    # 预定义的股票代码列表（示例）
    stock_symbols = [
        '000001.SZ', '600519.SH', '000002.SZ', '600036.SH',
        '601318.SH', '000858.SZ', '600000.SH', '000333.SZ',
        '600276.SH', '002415.SZ', '601899.SH', '002594.SZ',
        '600887.SH', '000651.SZ', '600585.SH', '002475.SZ',
        '601328.SH', '000063.SZ', '600030.SH', '000725.SZ'
    ]
    
    # 限制同步数量
    if limit > 0:
        stock_symbols = stock_symbols[:limit]
    
    logger.info(f"开始批量同步股票历史数据，共 {len(stock_symbols)} 只股票")
    
    success_count = 0
    failed_count = 0
    
    for i, symbol in enumerate(stock_symbols, 1):
        logger.info(f"进度: {i}/{len(stock_symbols)} - 处理股票: {symbol}")
        
        if sync_single_stock(symbol):
            success_count += 1
        else:
            failed_count += 1
        
        # 避免请求过于频繁
        time.sleep(0.5)
    
    logger.info(f"批量同步完成，成功: {success_count} 只，失败: {failed_count} 只")
    return {'success': success_count, 'failed': failed_count}


def main():
    """
    主函数，处理命令行参数并执行相应的同步操作
    """
    parser = argparse.ArgumentParser(description='股票历史数据同步工具')
    parser.add_argument('symbol', nargs='?', help='股票代码（可选，不指定则同步批量股票）')
    parser.add_argument('--limit', type=int, default=100, help='批量同步时限制的股票数量（默认: 100）')
    
    args = parser.parse_args()
    
    if args.symbol:
        # 同步单只股票
        result = sync_single_stock(args.symbol)
        if result:
            print(f"股票 {args.symbol} 同步成功")
        else:
            print(f"股票 {args.symbol} 同步失败")
    else:
        # 批量同步股票
        result = sync_all_stocks(args.limit)
        print(f"批量同步完成，成功: {result['success']} 只，失败: {result['failed']} 只")


if __name__ == "__main__":
    main()
