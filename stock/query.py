import itertools
import sqlalchemy as sql
import pandas as pd
from stock import models, util, api, params, predict as pp


def set_signals(codes, **kw):
    if not isinstance(codes, list):
        codes = [codes]
    filtered = {k: v for k, v in kw.items() if hasattr(models.Price, k)}
    if not filtered:
        return
    with models.session_scope() as s:
        for c in codes:
            s.query(models.Price).filter_by(quandl_code=c).update(
                filtered,
                synchronize_session=False,
            )


def get_quandl_code(code):
    q = models.QuandlCode
    with models.session_scope(expire_on_commit=False) as s:
        return s.query(q).filter_by(code=code).options(sql.orm.joinedload(q.signal)).first()


def get_quandl_codes(page=0, per_page=20, order_by=None, asc=True):
    if order_by:
        order_by = models.key_to_column(order_by)
    if order_by is None:
        order_by = models.QuandlCode.code
    if asc:
        order_by = order_by.asc()
    else:
        order_by = order_by.desc()
    q = models.QuandlCode
    with models.session_scope() as s:
        q = s.query(q).join(q.signal).options(
            sql.orm.joinedload(models.QuandlCode.signal).joinedload(models.Signal.price),
        )
        codes = q.order_by(order_by).offset(page * per_page).limit(per_page)
        # need when you returns Model objects directly after closing a session
        # but this removes all from session (no commits anymore)
        s.expunge_all()
        return codes


def imported_quandl_codes():
    with models.session_scope() as s:
        codes = [p[0] for p in s.query(models.Price.quandl_code).distinct().all()]
        # p[0] is string, so no need to expunge_all
    return codes


# NOTE: if codes == [], it takes a lot of time
def latest_prices_by_codes(codes=[]):
    p1 = models.Price
    p2 = sql.alias(models.Price)
    with models.session_scope() as s:
        query = s.query(p1).outerjoin(p2, sql.and_(
            p1.quandl_code == p2.c.quandl_code,
            p1.date < p2.c.date,
        )).filter(
            p1.quandl_code.in_(codes) if codes else True,
            p2.c.date.is_(None),
        )
        df = pd.read_sql(query.statement, query.session.bind, index_col="quandl_code")
    return df


def query_prices_by_codes(codes=[]):
    p1 = models.Price
    p2 = sql.alias(models.Price)
    with models.session_scope(expire_on_commit=False) as s:
        query = s.query(p1).join(p2, sql.and_(
            p1.quandl_code == p2.c.quandl_code,
            p1.date <= p2.c.date,
        )).filter(
            p1.quandl_code.in_(codes) if codes else True,
        ).group_by(
            p1.quandl_code,
            p1.date,
        ).having(
            sql.func.count("*") <= 2
        )
        return itertools.groupby(query.all(), key=lambda p: p.quandl_code)


def non_imported_quandl_codes(database_code):
    database_code = database_code.upper()  # FIXME
    codes = imported_quandl_codes()
    session = models.Session()
    allcodes = session.query(models.QuandlCode).filter_by(database_code=database_code).filter(
        models.QuandlCode.code.notin_([c.code for c in codes])
    ).all()
    session.close()
    return allcodes


def update_price_index(session, quandl_code, prices):
    change, change_percent = None, None
    if len(prices) == 2:
        price, prev = prices
        price_id, prev_id = price.id, prev.id
        change = price.close - prev.close
        change_percent = change / prev.close
    elif len(prices) == 1:
        price = prices[0]
        price_id, prev_id = price.id, None
    else:
        price_id, prev_id = None, None
    session.query(models.Signal).filter_by(quandl_code=quandl_code).update({
        "price_id": price_id,
        "previous_price_id": prev_id,
        "change": change,
        "change_percent": change_percent,
    }, synchronize_session=False)


def store_prices_if_needed(quandl_code, limit=None, force=False):
    quandl_code = quandl_code.upper()  # FIXME
    with models.session_scope() as s:
        data = s.query(models.Price).filter_by(quandl_code=quandl_code).first()
        if data and not force:
            return False
        s.query(models.Price).filter_by(quandl_code=quandl_code).delete()
    data = api.quandl.get_by_code(quandl_code)
    if limit:
        data = data.reindex(reversed(data.index))[:limit]

    data.to_sql("price", models.engine, if_exists='append')  # auto commit
    with models.session_scope() as s:
        prices = s.query(models.Price).filter_by(quandl_code=quandl_code).order_by(models.Price.date.desc()).limit(2).all()
        update_price_index(s, quandl_code, prices)
    return True


def create_quandl_codes_if_needed(database_code):
    database_code = database_code.upper()  # FIXME
    with models.session_scope(expire_on_commit=False) as s:
        qcodes = s.query(models.QuandlCode).filter_by(database_code=database_code).all()
        if not qcodes:
            codes = api.quandl.quandl_codes(database_code)
            qcodes = [models.QuandlCode(code=c) for c in codes]
            s.add_all(qcodes)
    return qcodes


# INTERFACEの統一とapiとしてjsonに変換する関数必要
# if price_type is None, return a DataFrame object instead of Series
def get(quandl_code, price_type="close", from_date=None, to_date=None, chart_type=None):
    quandl_code = quandl_code.upper().strip()
    from_date = util.str2date(from_date)
    to_date = util.str2date(to_date)

    with models.session_scope() as s:
        query = s.query(models.Price).filter_by(quandl_code=quandl_code)
        if from_date:
            query = query.filter(models.Price.date >= from_date)
        if to_date:
            query = query.filter(models.Price.date <= to_date)
        df = pd.read_sql(query.statement, query.session.bind, index_col="date")

    if price_type is None:
        return df

    series = getattr(df, price_type)

    if chart_type:
        f = params.get_lines()[chart_type]
        series = f(series)

    return series


def predict(quandl_code, *args, **kw):
    df = get(quandl_code, price_type=None, **kw)
    return pp.predict(df)


def get_all(from_date=None, to_date=None):
    with models.session_scope() as s:
        q = s.query(models.Price)
        if from_date:
            q = q.filter(models.Price.date >= from_date)
        if to_date:
            q = q.filter(models.Price.date <= to_date)
        df = pd.read_sql(q.statement, q.session.bind, index_col=["quandl_code", "date"])
        return df
