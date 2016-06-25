import pandas as pd
import quandl

from stock import models
from stock import constant as C


# for now, backend should not store any data on heroku

def get_from_quandl(quandl_code, last_date=None, price_type=None):
    session = models.Session()
    data = session.query(models.Price).filter_by(quandl_code=quandl_code).first()
    if data:
        query = session.query(models.Price).filter_by(quandl_code=quandl_code)
        return pd.read_sql(query.statement, query.session.bind, index_col="date")
    else:
        mydata = quandl.get(quandl_code)
        mydata = mydata.rename(columns=C.MAP_PRICE_COLUMNS)

        # series = getattr(df, price_type.name)
        mydata = mydata[pd.isnull(mydata.close) == False]
        mydata['quandl_code'] = quandl_code
        # mydata['code'] = quandl_code

        mydata.to_sql("price", models.engine, if_exists='append')
        return mydata


def get_db():
    session = models.Session()
    return session.query(models.QuandlDatabase).all()


def get():
    session = models.Session()
    return session.query(models.QuandlCode).all()


def first(code):
    session = models.Session()
    return session.query(models.QuandlCode).filter_by(code=code).first()
