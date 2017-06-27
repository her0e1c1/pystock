import collections
import pandas as pd
from stock import models, signals, charts, util, api


def quandl_codes():
    session = models.Session()
    codes = [p[0] for p in session.query(models.Price.quandl_code).distinct().all()]
    session.close()
    return codes


def non_imported_quandl_codes(database_code):
    database_code = database_code.upper()  # FIXME
    codes = quandl_codes()
    session = models.Session()
    allcodes = session.query(models.QuandlCode).filter_by(database_code=database_code).filter(
        models.QuandlCode.code.notin_([c.code for c in codes])
    ).all()
    session.close()
    return allcodes


def store_prices_if_needed(quandl_code, limit=None, force=False):
    quandl_code = quandl_code.upper()  # FIXME
    session = models.Session()
    data = session.query(models.Price).filter_by(quandl_code=quandl_code).first()
    if data:
        if not force:
            return False
        session.query(models.Price).filter_by(quandl_code=quandl_code).delete()
        session.commit()
        session.close()
    data = api.quandl.get_by_code(quandl_code)
    if limit:
        data = data.reindex(reversed(data.index))[:limit]
    data.to_sql("price", models.engine, if_exists='append')  # auto commit
    return True


def create_quandl_codes_if_needed(database_code):
    database_code = database_code.upper()  # FIXME
    session = models.Session()
    qcodes = session.query(models.QuandlCode).filter_by(database_code=database_code).all()
    if not qcodes:
        codes = api.quandl.quandl_codes(database_code)
        qcodes = [models.QuandlCode(code=c) for c in codes]
        session.add_all(qcodes)
        session.commit()
    return qcodes


# INTERFACEの統一とapiとしてjsonに変換する関数必要
# if price_type is None, return a DataFrame object instead of Series
def get(quandl_code, price_type="close", from_date=None, to_date=None, chart_type=None):
    quandl_code = quandl_code.upper().strip()

    if from_date:
        from_date = util.str2date(from_date)
    if to_date:
        to_date = util.str2date(to_date)

    Price = models.Price
    session = models.Session()
    query = session.query(Price).filter_by(quandl_code=quandl_code)
    if from_date:
        query = query.filter(Price.date >= from_date)
    if to_date:
        query = query.filter(Price.date <= to_date)

    df = pd.read_sql(query.statement, query.session.bind, index_col="date")  # queryの戻り値に出来る?

    if price_type is None:
        return df

    series = getattr(df, price_type)

    if chart_type:
        f = getattr(charts, chart_type)
        series = f(series)

    session.close()
    return series


# TODO: 並列化
def signal(signal=None, *args, **kw):
    if signal is None:
        signal = "rolling_mean"
    result = collections.defaultdict(list)
    for code in quandl_codes():
        series = get(code, **kw)
        f = getattr(signals, signal)
        buy_or_sell = f(series, *args)
        if buy_or_sell:
            result[buy_or_sell].append(code)
    return result


def predict(quandl_code, *args, **kw):
    df = get(quandl_code, price_type=None, **kw)
    return signals.predict(df)
