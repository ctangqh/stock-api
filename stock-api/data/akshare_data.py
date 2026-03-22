import akshare as ak
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class AkShareData:
    def __init__(self):
        pass

    def get_stock_latest_price(self, symbol: str) -> float:
        try:
            logger.info(f"获取股票最新价格，symbol: {symbol}")
            stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol=symbol)
            df = pd.DataFrame(stock_bid_ask_em_df)
            latest_price = df.loc[df['item'] == '最新', 'value'].values[0]
            logger.info(f"获取到股票最新价格，symbol: {symbol}, price: {latest_price}")
            return float(latest_price)
        except Exception as e:
            logger.exception(f"获取股票最新价格失败，symbol: {symbol}, 错误: {str(e)}")
            latest_price = 0
            return latest_price

