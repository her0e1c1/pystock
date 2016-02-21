# coding: utf-8
import pandas as pd

from stock import query
from stock import wrapper
from stock import util


def last_date():
    return util.last_date()


def make_data_frame(day_info_query):
    return pd.DataFrame(
        [(info.w.js_datetime, info.w.closing) for info in day_info_query],
        columns=["date", "closing"]
        )


def scrape_and_store(min_id=1, max_id=None, start=None, end=None,
                     each=False, ignore=False, last_date=None):
    if max_id is None:
        max_id = Company.max_id()
    for id in range(min_id, max_id + 1):
        set(id, each=each, ignore=True, last_date=last_date)


def get_companies(ratio_closing_minus_rolling_mean_25=None,
                  closing_rsi_14=None):
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
    return q.all()


def update_search_fields():
    closing_minus_rolling_mean_25()
    closing_rsi_14()


def closing_minus_rolling_mean_25(period=25):
    """長期移動平均線と現在の株価の差を予め計算"""
    session = query.models.Session()
    for company in query.Company.query(session):
        df = make_data_frame(query.DayInfo.get(company_id=company.id, session=session))
        closing = df.closing.tail(1)
        mean = pd.rolling_mean(df.closing, period).tail(1)
        if closing.empty or mean.empty:
            continue
        ratio = float((closing - mean) / closing) * 100
        if company.search_field is None:
            sf = query.models.CompanySearchField()
        else:
            sf = company.search_field
        sf.ratio_closing_minus_rolling_mean_25 = ratio
        company.search_field = sf
        session.add(company)
    session.commit()
    session.close()


def closing_rsi_14(period=14):
    """営業最終日のRSIを求める"""
    session = query.models.Session()
    for company in query.Company.query(session):
        df = make_data_frame(query.DayInfo.get(company_id=company.id, session=session))
        rsi = wrapper.RSI(df.closing, period)
        if rsi.empty:
            continue
        last_rsi = float(rsi[rsi.last_valid_index()])
        if company.search_field is None:
            sf = query.models.CompanySearchField()
        else:
            sf = company.search_field
        sf.closing_rsi_14 = last_rsi
        company.search_field = sf
        session.add(company)
    session.commit()
    session.close()
