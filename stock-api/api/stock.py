# from util.PgDBUtil import PgDBUtil
import akshare as ak
import pandas as pd

def stock_individual_fund_flow():
    index_global_spot_em_df = ak.index_global_spot_em()
    df = pd.DataFrame(index_global_spot_em_df)
    df = df[df['代码'].isin(['DJIA','NDX'])]
    print(df.to_json())
    # df.to_csv("index_global_spot_em.csv", index=False)
    print(df)

# 热门股票
# https://push2.eastmoney.com/api/qt/ulist/get?fltt=1&invt=2&cb=jQuery35108636826194364327_1770455869297&fields=f14%2Cf12%2Cf13%2Cf1%2Cf2%2Cf4%2Cf3%2Cf152&secids=0.002506%2C1.603881%2C1.603618%2C0.002361%2C1.600759%2C0.002519%2C0.002342%2C1.603667%2C0.002015%2C0.002155%2C1.600884%2C0.002957%2C0.002131%2C0.002009%2C0.002112%2C0.002413%2C1.600519%2C0.002455%2C0.300059&ut=fa5fd1943c7b386f172d6893dbfba10b&pn=1&np=1&pz=20&dect=1&wbp2u=%7C0%7C0%7C0%7Cweb&_=1770455869331
# 个股资金排名
# https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112302209664431469499_1770456390556&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
# https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery11230919858424235644_1770456637056&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
# https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery11230919858424235644_1770456637056&fid=f72&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
# https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery11230919858424235644_1770456637056&fid=f72&po=1&pz=50&pn=2&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13

# 大盘信息
# https://push2.eastmoney.com/api/qt/ulist.np/get?cb=jQuery11230806474628323575_1770647354626&fltt=2&secids=1.000001%2C0.399001&fields=f1%2Cf2%2Cf3%2Cf4%2Cf6%2Cf12%2Cf13%2Cf104%2Cf105%2Cf106&ut=b2884a393a59ad64002292a3e90d46a5&_=1770647354627
if __name__ == '__main__':
    get_stock_info('000001')