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


def update_copmany_list(start=None, end=None, each=False, ignore=False, last_date=None, limit=None):
    session = Session(ignore=ignore, each=each)
    for c in query.Company.all(last_date=last_date, session=session._s, limit=limit):
        if not c:
            logger.info("SKIP: company(id=%s)" % c.id)
            continue

        def add_instance(**kw):
            kw["company_id"] = c.id
            return models.DayInfo(**kw)

        history = get_scraper().history(c.code, start, end)
        session.each(history, add_instance)
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
    val = kw[col_name]
    col = getattr(query.models.CompanySearchField, col_name)
    if val >= 0:
        q = q.filter(col >= val)
    else:
        q = q.filter(col < val)
    return q


def get(**kw):
    session = query.models.Session()
    q = query.Company.query(session)
    if any(kw.values()):
        q = q.join(query.models.Company.search_field)

    if kw["ratio_closing_minus_rolling_mean_25"] is not None:
        q = _percent(q, kw, "ratio_closing_minus_rolling_mean_25")

    if kw["ratio_closing1_minus_closing2"] is not None:
        q = _percent(q, kw, "ratio_closing1_minus_closing2")

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

    if kw["closing_macd_minus_signal"] is not None:
        col_name1 = "closing_macd_minus_signal1_26_12_9"
        col_name2 = "closing_macd_minus_signal2_26_12_9"
        v = kw["closing_macd_minus_signal"]
        col1 = getattr(query.models.CompanySearchField, col_name1)
        col2 = getattr(query.models.CompanySearchField, col_name2)
        if v > 0:
            q = q.filter(col1 >= 0)
            q = q.filter(col2 <= 0)
        else:
            q = q.filter(col1 <= 0)
            q = q.filter(col2 >= 0)

    if kw["closing_stochastic_d_minus_sd"] is not None:
        col_name1 = "closing_stochastic_d_minus_sd1_14_3_3"
        col_name2 = "closing_stochastic_d_minus_sd2_14_3_3"
        v = kw["closing_stochastic_d_minus_sd"]
        col1 = getattr(query.models.CompanySearchField, col_name1)
        col2 = getattr(query.models.CompanySearchField, col_name2)
        if v > 0:
            q = q.filter(col1 >= 0)
            q = q.filter(col2 <= 0)
        else:
            q = q.filter(col1 <= 0)
            q = q.filter(col2 >= 0)

    return q.all()
