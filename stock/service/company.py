# coding: utf-8
import io

import requests
from flask import abort

from stock import query
from stock import models
from stock import config as C

from .session import Session

from logging import getLogger
logger = getLogger(__name__)


def get_scraper():
    from stock.scrape import YahooJapan
    return YahooJapan()


def update_copmany(id, start=None, end=None):
    with Session() as s:
        c = query.Company.query(session=s).first(id=id)
        _update_copmany(s, c, start=start, end=end)


def _update_copmany(session, company, start=None, end=None):
    if not company:
        logger.info("SKIP: company(id=%s)" % company.id)
        return

    def add_instance(**kw):
        kw["company_id"] = company.id
        return models.DayInfo(**kw)

    # 1日だけ更新する場合でも複数ページにアクセスしている(無駄)
    history = get_scraper().history(company.code, start, end)
    session.each(history, add_instance)


def update_copmany_list(start=None, end=None, each=False, ignore=False, last_date=None, limit=None):
    session = Session(ignore=ignore, each=each)
    for c in query.Company.all(last_date=last_date, session=session._s, limit=limit):
        _update_copmany(session, c)
    session.close()


def download_company_list(url=C.COMPANY_XLS_URL):
    from stock.cmd.import_company import Reader
    resp = requests.get(url)
    if resp.ok:
        return Reader(filepath=io.BytesIO(resp.content))


def download_and_store_company_list(url=C.COMPANY_XLS_URL):
    reader = download_company_list(url)
    if reader:
        return reader.store()
    else:
        return False


def first(id, raise_404=False):
    company = query.Company.first(id=id)
    if not company and raise_404:
        abort(404)
    return company


def _percent(q, kw, col_name):
    if col_name not in kw or kw[col_name] is None:
        return q
    val = kw[col_name]
    col = getattr(query.models.CompanySearchField, col_name)
    if val >= 0:
        q = q.filter(col >= val)
    else:
        q = q.filter(col < val)
    return q


def _cross(q, kw, val_name, format_col_name):
    if val_name not in kw or kw[val_name] is None:
        return q

    col_name1 = format_col_name % 1
    col_name2 = format_col_name % 2
    v = kw[val_name]
    col1 = getattr(query.models.CompanySearchField, col_name1)
    col2 = getattr(query.models.CompanySearchField, col_name2)
    if v > 0:
        # Golden cross
        q = q.filter(col1 >= 0)
        q = q.filter(col2 <= 0)
    else:
        # Dead cross
        q = q.filter(col1 <= 0)
        q = q.filter(col2 >= 0)
    return q


def get(**kw):
    session = query.models.Session()
    q = query.Company.query(session)
    if any(kw.values()):
        q = q.join(query.models.Company.search_field)

    q = _percent(q, kw, "ratio_closing_minus_rolling_mean_25")
    q = _percent(q, kw, "ratio_closing1_minus_closing2")

    q = _cross(q, kw, "closing_stochastic_d_minus_sd", "closing_stochastic_d_minus_sd%d_14_3_3")
    q = _cross(q, kw, "closing_macd_minus_signal", "closing_macd_minus_signal%d_26_12_9")

    if kw["closing_rsi_14"] is not None:
        rsi = kw["closing_rsi_14"]
        col = query.models.CompanySearchField.closing_rsi_14
        if rsi >= 0:
            q = q.filter(col >= rsi)
        else:
            rsi *= -1
            q = q.filter(col < rsi)

    if kw["interval_closing_bollinger_band_20"] is not None:
        col_name = "interval_closing_bollinger_band_20"
        v = kw["interval_closing_bollinger_band_20"]
        col = getattr(query.models.CompanySearchField, col_name)
        q = q.filter(col == v)

    return q.all()
