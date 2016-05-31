import datetime

import enum
import pandas as pd
import quandl

import matplotlib.pyplot as plt

from stock import models
from stock.service.simulate import RollingMean, MACD
from stock.service.simulate import timing


DEFAULT_ROLLING_MEAN_RATIO = 5

class PriceType(enum.Enum):
    open = "open"
    low = "low"
    high = "high"
    close = "close"


MAP_TO_COLUMNS = {
    "Open Price": "open",
    "Close Price": "close",
    "High Price": "high",
    "Low Price": "low",
}

# どれを一番良い結果として取るかも、問題となる
# 3か月売買での平均とかの方がいいかも(長期の計算は、次も当てはまるとは限らない)
# 最終結果だけでなく、平均的に儲けているものが、良いかも

# start/end dateを加える(index)

DATE_FORMATS = ["%Y/%m/%d", "%Y-%m-%d"]
def str_to_date(s):
    for fmt in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except:
            pass
    else:
        raise ValueError


def s(quandl_code="NIKKEI/INDEX", price_type=PriceType.close, way=None, lostcut=3, start=None, end=None, **kw):
    if isinstance(start, str):
        start = str_to_date(start)
    if isinstance(end, str):
        end = str_to_date(end)
    if not isinstance(price_type, enum.Enum):
        price_type = PriceType(price_type)
    df = get_from_quandl(quandl_code, last_date=None)
    series = getattr(df, price_type.name)
    series = series.ix[start:end]

    r = 0
    df = None
    # 一番儲けらるもの(パラメータの調節が必要なものもある.) and / or もできるようにしたい
    lists = [MACD(series)] + [RollingMean(series, i) for i in range(1, 10)]
    for l in lists:
        df_result = l.simulate_action()
        if df_result.empty:
            continue
        accumulation = df_result.ix[-1].accumulation
        if r < accumulation:
            r = max(r, accumulation)
            df = l
    return (r, df)


def create():
    models.Base.metadata.create_all()


def drop():
    models.Base.metadata.drop_all()


# 元のグラフも表示した方がわかりやすい
# or use `df.plot()`
def drow(df):
    plt.figure(figsize=(15, 15))
    pass



# 使用できるqcodeを表示できるの？

# interface
# PriceFrame(qcode="XXX").open.rolling_mean(25).plot()



def chart(qcode="NIKKEI/INDEX", price_type=PriceType.close, way=None, lostcut=3, **kw):
    if not isinstance(price_type, enum.Enum):
        price_type = PriceType(price_type)
    df = get_from_quandl(qcode, last_date=None)
    series = getattr(df, price_type.name)
    return MACD(series)
    return RollingMean(series, ratio=kw.get("ratio", DEFAULT_ROLLING_MEAN_RATIO))


def simulate(qcode="NIKKEI/INDEX", price_type=PriceType.close, way=None, **kw):
    if not isinstance(price_type, enum.Enum):
        price_type = PriceType(price_type)
    df = get_from_quandl(qcode, last_date=None)
    series = getattr(df, price_type.name)
    return RollingMean(series, ratio=kw.get("ratio", DEFAULT_ROLLING_MEAN_RATIO)).simulate()



# TODO: use sqlite3
def get_from_quandl(qcode, last_date=None, price_type=PriceType.close):
    session = models.Session()
    data = session.query(models.Price).filter_by(qcode=qcode).first()
    if data:
        query = session.query(models.Price).filter_by(qcode=qcode)
        return pd.read_sql(query.statement, query.session.bind, index_col="date")
    else:
        mydata = quandl.get(qcode)
        mydata = mydata.rename(columns=MAP_TO_COLUMNS)
        # series = getattr(df, price_type.name)
        mydata = mydata[pd.isnull(mydata.open) == False]
        mydata['qcode'] = qcode
        mydata.to_sql("price", models.engine, if_exists='append')
        return mydata


def show(kw):
    from stock.service.simulate import RollingMean
    qcode = "NIKKEI/INDEX"
    s = models.Session()
    data = s.query(models.Price).filter_by(qcode=qcode).all()
    if data:
        query = s.query(models.Price).filter_by(qcode=qcode)
        mydata = pd.read_sql(query.statement, query.session.bind, index_col="date")
    else:
        mydata = quandl.get(qcode)
        # mydata[mydata.columns[0]]
        columns = {
            "Open Price": "open",
            "Close Price": "close",
            "High Price": "high",
            "Low Price": "low",
        }
        mydata = mydata.rename(columns=columns)
        mydata = mydata[pd.isnull(mydata.open) == False]
        mydata['qcode'] = qcode
        mydata.to_sql("price", models.engine, if_exists='append')  # not need to commit

    series = mydata.open
    print(RollingMean(series, ratio=kw.get("ratio")).simulate())
