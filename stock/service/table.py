import pandas as pd
import quandl
from stock import models


def create():
    models.Base.metadata.create_all()


def drop():
    models.Base.metadata.drop_all()


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
        # columns = {
        #     "Open Price": "open",
        #     "Close Price": "close",
        #     "High Price": "high",
        #     "Low Price": "low",
        #      "Volume": "volume",
        # }
        mydata = mydata.rename(columns=columns)
        mydata = mydata[pd.isnull(mydata.open) == False]
        mydata['qcode'] = qcode
        mydata.to_sql("price", models.engine, if_exists='append')  # not need to commit

    series = mydata.open
    print(RollingMean(series, ratio=kw.get("ratio")).simulate())
