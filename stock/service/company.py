# coding: utf-8
import io

import requests

from stock import query
from stock import models
from stock import config as C

from .session import session_each

from logging import getLogger
logger = getLogger(__name__)


def get_scraper():
    from stock.scrape import YahooJapan
    return YahooJapan()


def update_copmany_list(start=None, end=None, each=False, ignore=False, last_date=None, limit=None):
    session = query.models.Session()
    for c in query.Company.all(last_date=last_date, session=session, limit=limit):
        if not c:
            logger.info("SKIP: company(id=%s)" % c.id)
            continue

        def add_instance(**kw):
            kw["company_id"] = c.id
            return models.DayInfo(**kw)

        history = get_scraper().history(c.code, start, end)
        session_each(history, add_instance, session=session, ignore=ignore, each=each)
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


def get(ratio_closing_minus_rolling_mean_25=None,
        closing_rsi_14=None,
        interval_closing_bollinger_band_20=None,
        closing_stochastic_d_minus_sd=None,
        closing_macd_minus_signal=None):
    session = query.models.Session()
    q = query.Company.query(session)

    if ratio_closing_minus_rolling_mean_25 is not None:
        ratio = ratio_closing_minus_rolling_mean_25
        q = q.join(query.models.Company.search_field)
        col = query.models.CompanySearchField.ratio_closing_minus_rolling_mean_25
        if ratio >= 0:
            q = q.filter(col >= ratio)
        else:
            q = q.filter(col < ratio)

    if closing_rsi_14 is not None:
        rsi = closing_rsi_14
        q = q.join(query.models.Company.search_field)
        col = query.models.CompanySearchField.closing_rsi_14
        if rsi >= 0:
            q = q.filter(col >= rsi)
        else:
            rsi *= -1
            q = q.filter(col < rsi)

    if interval_closing_bollinger_band_20 is not None:
        col_name = "interval_closing_bollinger_band_20"
        v = interval_closing_bollinger_band_20
        q = q.join(query.models.Company.search_field)
        col = getattr(query.models.CompanySearchField, col_name)
        q = q.filter(col == v)

    if closing_macd_minus_signal is not None:
        col_name1 = "closing_macd_minus_signal1_26_12_9"
        col_name2 = "closing_macd_minus_signal2_26_12_9"
        v = closing_macd_minus_signal
        q = q.join(query.models.Company.search_field)
        col1 = getattr(query.models.CompanySearchField, col_name1)
        col2 = getattr(query.models.CompanySearchField, col_name2)
        if v > 0:
            q = q.filter(col1 >= 0)
            q = q.filter(col2 <= 0)
        else:
            q = q.filter(col1 <= 0)
            q = q.filter(col2 >= 0)

    if closing_stochastic_d_minus_sd is not None:
        col_name1 = "closing_stochastic_d_minus_sd1_14_3_3"
        col_name2 = "closing_stochastic_d_minus_sd2_14_3_3"
        v = closing_stochastic_d_minus_sd
        q = q.join(query.models.Company.search_field)
        col1 = getattr(query.models.CompanySearchField, col_name1)
        col2 = getattr(query.models.CompanySearchField, col_name2)
        if v > 0:
            q = q.filter(col1 >= 0)
            q = q.filter(col2 <= 0)
        else:
            q = q.filter(col1 <= 0)
            q = q.filter(col2 >= 0)

    return q.all()
