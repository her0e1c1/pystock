# coding: utf-8
import pandas as pd

from .session import Session
from stock.service import chart


def last(series, offset_from_last=0):
    i = series.last_valid_index()
    if i is None:
        return
    elif i - offset_from_last >= 0:
        return series[i - offset_from_last]


def increment(a, b):
    if a is None or b is None:
        return
    elif a.is_integer() and b.is_integer():
        return float((a - b) / b) * 100


def with_session(f, col_name):
    with Session() as s:
        s.with_session(f, col_name)


def update_search_fields():
    closing_minus_rolling_mean_25()
    closing_rsi_14()
    closing_macd_minus_signal()
    low_min()
    closing_stochastic_d_minus_sd()
    ratio_sigma_low_minus_closing()


def closing_minus_rolling_mean_25(period=25):
    """長期移動平均線と現在の株価の差を予め計算"""
    def f(df):
        mean = pd.rolling_mean(df.closing, period)
        return increment(last(df.closing), last(mean))

    with_session(f, "ratio_closing_minus_rolling_mean_25")


def closing_rsi_14(period=14):
    """営業最終日のRSIを求める"""
    def f(df):
        rsi = chart.rsi(df.closing, period)
        if not rsi.empty:
            return float(rsi[rsi.last_valid_index()])
    with_session(f, "closing_rsi_14")


def closing_macd_minus_signal():
    def wrap(index):
        def last(p):
            lvi = p.last_valid_index()
            if lvi and lvi > 0:
                return p[lvi - (index - 1)]

        def f(df):
            macd = last(chart.macd_line(df.closing))
            signal = last(chart.macd_signal(df.closing))
            if macd is not None and signal is not None:
                return float(macd - signal)
        return f
    with_session(wrap(1), "closing_macd_minus_signal1_26_12_9")
    with_session(wrap(2), "closing_macd_minus_signal2_26_12_9")


def low_min():
    def wrap(index):
        def f(df):
            v = float(df.low.tail(index).min())
            if not pd.isnull(v):
                return v
        return f
    with_session(wrap(25), "low_min_25")
    with_session(wrap(75), "low_min_75")
    with_session(wrap(200), "low_min_200")


def closing_bollinger_band(period=20):
    def f(df):
        prices = df.closing
        if prices.empty:
            return None
        p = float(prices.tail(1))
        mean = float(pd.rolling_mean(prices, period).tail(1))
        std = float(pd.rolling_std(prices, period).tail(1))
        if pd.isnull(mean) or pd.isnull(std):
            return None
        if p == mean:
            return 0
        sign = 1 if p > mean else -1
        for sigma in [1, 2, 3]:
            m1 = mean + sign * std * (sigma - 1)
            m2 = mean + sign * std * sigma
            if min(m1, m2) < p <= max(m1, m2):
                return sign * sigma
    with_session(f, "interval_closing_bollinger_band_20")


def closing_stochastic_d_minus_sd():
    def wrap(index):
        def last(p):
            lvi = p.last_valid_index()
            if lvi and lvi > 0:
                return p[lvi - (index - 1)]

        def f(df):
            k, d, sd = 14, 3, 3
            fast = last(chart.stochastic_d(df.closing, k=k, d=d))
            slow = last(chart.stochastic_sd(df.closing, k=k, d=d, sd=sd))
            if fast is not None and slow is not None:
                return float(fast - slow)
        return f
    with_session(wrap(1), "closing_stochastic_d_minus_sd1_14_3_3")
    with_session(wrap(2), "closing_stochastic_d_minus_sd2_14_3_3")


def ratio_closing1_minus_closing2():
    def f(df):
        c0 = last(df.closing)
        c1 = last(df.closing, 1)
        return increment(c0, c1)

    with_session(f, "ratio_closing1_minus_closing2")


def ratio_sigma_low_minus_closing(period=20):
    """
    安値と前の日の終値の割合を求める。
    ボリンジャーバンドの考え方を応用して、次の日の安値を求める.
    """
    def wrap(index):
        def f(df):
            c = df.closing.shift(1)
            l = df.low
            d = (l - c)
            d = d[d < 0][:period]
            f = float(d.mean() - index * d.std())
            li = c.last_valid_index()
            if li:
                l = float(c[li])
                if not pd.isnull(f) and not pd.isnull(l):
                    return l + f
        return f
    with_session(wrap(1), "ratio_1sigma_low_minus_closing")
    with_session(wrap(2), "ratio_2sigma_low_minus_closing")
