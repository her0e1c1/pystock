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
