# coding: utf-8
import datetime

import sqlalchemy as sql
import pandas as pd


class Query(object):

    def __init__(self, q):
        self.q = q

    def __iter__(self):
        return iter(self.q)

    def __getattr__(self, name):
        attr = getattr(self.q, name)
        if callable(attr):
            def f(*args, **kw):
                r = attr(*args, **kw)
                if isinstance(r, sql.orm.query.Query):
                    return self.__class__(r)
                else:
                    return r
            return f
        else:
            return attr


def to_seq(dates, series):
    return list([a, b] for a, b
                in zip(dates.values.tolist(), series.values.tolist())
                if not pd.isnull(b))


class DayInfoQuery(Query):

    def df(self):
        from stock.service import make_data_frame
        return make_data_frame(self)

    def rolling_mean(self, period=30):
        df = self.df()
        mean = pd.rolling_mean(df.closing, period)
        return list([a, b] for a, b in zip(df.date.values.tolist(), mean.values.tolist())
                    if not pd.isnull(b))

    def macd_line(self):
        df = self.df()
        return to_seq(df.date, macd_line(df.closing))

    def macd_signal(self):
        df = self.df()
        return to_seq(df.date, macd_signal(df.closing))

    def RSI(self, period):
        df = self.df()
        rsi = RSI(df.closing, period)
        return list([a, b] for a, b in zip(df.date.values.tolist(), rsi.values.tolist())
                    if not pd.isnull(b))

    def ohlc(self):
        return [(d["date"], d["opening"], d["high"], d["low"], d["closing"])
                for d in self.df().to_dict(orient="records")]

    def volume(self):
        df = self.df()
        return list(zip(df.date.values.tolist(),
                        df.volume.values.tolist()))

    def closing(self):
        df = self.df()
        return list(zip(df.date.values.tolist(),
                        df.closing.values.tolist()))

    def to_series(self, type="closing"):
        return [(info.w.js_datetime, info.w.closing) for info in self]


class Wrapper(object):

    def __init__(self, ins):
        from . import models  # Not cyclic import
        assert isinstance(ins, getattr(models, self.__class__.__name__))
        self.ins = ins

    # company_idみたいに、定義されていない属性はinsから取得
    def __getattr__(self, name):
        return getattr(self.ins, name)

    def to_dict(self):
        assert getattr(self, "dict_keys", False), "Must need a dict_keys attribute"
        return {k: getattr(self, k) for k in self.dict_keys}


class Company(Wrapper):
    dict_keys = ["id", "name", "code"]

    def fix_data_frame(self):
        data_records = []
        for day_info in self.day_info_list:
            data = {
                "high": day_info.fix_high(),
                "low": day_info.fix_low(),
                "opening": day_info.fix_opening(),
                "closing": day_info.fix_closing(),
                "date": day_info.js_datetime}
            data_records.append(data)
        return pd.DataFrame.from_records(data_records)


def macd_line(prices, fast=26, slow=12, signal=9):
    # Chris Manning (fast, slow, signal) = (17, 9, 7)
    return pd.ewma(prices, span=slow) - pd.ewma(prices, span=fast)


def macd_signal(prices, fast=26, slow=12, signal=9):
    return pd.ewma(macd_line(prices, fast=fast, slow=slow, signal=signal), span=signal)


def RSI(prices, period=14):
    # fill 0 at the first day
    diff = (prices - prices.shift(1)).fillna(0)

    def calc(p):
        gain =  p[p > 0].sum() / period
        loss = -p[p < 0].sum() / period
        rs = gain / loss
        return 100 - 100/(1+rs)

    return pd.rolling_apply(diff, period, calc)


class DayInfo(Wrapper):

    dict_keys = ["high", "low", "opening", "closing", "company_id", "js_datetime"]

    def _fix_value(self, value):
        for date in self.ins.company.split_stock_dates:
            if self.date < date.date:
                value *= date.from_number / float(date.to_number)
        return value

    @property
    def high(self):
        return self._fix_value(self.ins.high)

    @property
    def low(self):
        return self._fix_value(self.ins.low)

    @property
    def opening(self):
        return self._fix_value(self.ins.opening)

    @property
    def closing(self):
        return self._fix_value(self.ins.closing)

    @property
    def js_datetime(self):
        japan = self.ins.date + datetime.timedelta(hours=9)
        return int(japan.strftime("%s")) * 1000
