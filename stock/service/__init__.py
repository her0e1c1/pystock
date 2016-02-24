# coding: utf-8
import pandas as pd

from stock import query
from stock import wrapper
from stock import util

from . import company  # NOQA


def last_date():
    return util.last_date()


def make_data_frame(day_info_query):
    return pd.DataFrame(
        [(info.w.js_datetime, info.w.closing, info.w.volume,
            info.w.opening, info.w.high, info.w.low)
            for info in day_info_query],
        columns=["date", "closing", "volume", "opening", "high", "low"]
    )


def scrape_and_store(min_id=1, max_id=None, start=None, end=None,
                     each=False, ignore=False, last_date=None):
    if max_id is None:
        max_id = Company.max_id()
    for id in range(min_id, max_id + 1):
        set(id, each=each, ignore=True, last_date=last_date)


def get_companies(ratio_closing_minus_rolling_mean_25=None,
                  closing_rsi_14=None,
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

    return q.all()


def update_search_fields():
    closing_minus_rolling_mean_25()
    closing_rsi_14()
    closing_macd_minus_signal()


def closing_minus_rolling_mean_25(period=25):
    """長期移動平均線と現在の株価の差を予め計算"""
    def f(df):
        closing = df.closing.tail(1)
        mean = pd.rolling_mean(df.closing, period).tail(1)
        if not (closing.empty or mean.empty):
            return float((closing - mean) / closing) * 100

    with_session(f, "ratio_closing_minus_rolling_mean_25")


def closing_rsi_14(period=14):
    """営業最終日のRSIを求める"""
    def f(df):
        rsi = wrapper.RSI(df.closing, period)
        if not rsi.empty:
            return float(rsi[rsi.last_valid_index()])
    with_session(f, "closing_rsi_14")


def with_session(f, col_name, session=None):
    session = session or query.models.Session()
    for c in query.Company.query(session):
        df = make_data_frame(query.DayInfo.get(company_id=c.id, session=session))
        value = f(df)
        if value is None:
            continue
        if c.search_field is None:
            sf = query.models.CompanySearchField()
        else:
            sf = c.search_field
        setattr(sf, col_name, value)
        c.search_field = sf
        session.add(c)
    session.commit()
    session.close()


def closing_macd_minus_signal():
    def wrap(index):
        def last(p):
            lvi = p.last_valid_index()
            if lvi and lvi > 0:
                return p[lvi - (index - 1)]

        def f(df):
            macd = last(wrapper.macd_line(df.closing))
            signal = last(wrapper.macd_signal(df.closing))
            if macd is not None and signal is not None:
                return float(macd - signal)
        return f
    with_session(wrap(1), "closing_macd_minus_signal1_26_12_9")
    with_session(wrap(2), "closing_macd_minus_signal2_26_12_9")
