# coding: utf-8
import datetime

import pandas as pd


def to_seq(dates, series):
    return list([a, b] for a, b
                in zip(dates.values.tolist(), series.values.tolist())
                if not pd.isnull(b))


class DayInfoQuery(object):

    def __init__(self, q):
        self.query = q

    def df(self):
        from stock.service.day_info import make_data_frame
        return make_data_frame(self.query)

    def rolling_mean(self, period=30):
        df = self.df()
        return to_seq(df.date, pd.rolling_mean(df.closing, period))

    def bollinger_band(self, period=20, sigma=2):
        from stock.service import chart
        df = self.df()
        return to_seq(df.date, chart.bollinger_band(df.closing, period, sigma))

    def macd_line(self):
        from stock.service import chart
        df = self.df()
        return to_seq(df.date, chart.macd_line(df.closing))

    def macd_signal(self):
        from stock.service import chart
        df = self.df()
        return to_seq(df.date, chart.macd_signal(df.closing))

    def stochastic_k(self):
        from stock.service import chart
        df = self.df()
        return to_seq(df.date, chart.stochastic_k(df.closing, k=14))

    def stochastic_d(self):
        from stock.service import chart
        df = self.df()
        return to_seq(df.date, chart.stochastic_d(df.closing, k=14, d=3))

    def stochastic_sd(self):
        from stock.service import chart
        df = self.df()
        return to_seq(df.date, chart.stochastic_sd(df.closing, k=14, d=3, sd=3))

    def RSI(self, period):
        from stock.service import chart
        df = self.df()
        return to_seq(df.date, chart.rsi(df.closing, period))

    def ohlc(self):
        return [(d["date"], d["opening"], d["high"], d["low"], d["closing"])
                for d in self.df().to_dict(orient="records")]

    def volume(self):
        df = self.df()
        return to_seq(df.date, df.volume)

    def to_series(self):
        bbands = [{"name": "%dsigma" % s,
                   "data": self.bollinger_band(sigma=s),
                   "color": "black",
                   "yAxis": 0,
                   "lineWidth": 0.5}
                  for s in [3, 2, 1, -1, -2, -3]]

        # tooltip={valueDecimals: 2}
        return bbands + [
            {"name": "rolling_mean25", "data": self.rolling_mean(period=25)},
            {"name": "rolling_mean5", "data": self.rolling_mean(period=5)},
            {"name": "OHLC", "data": self.ohlc(), "type": "candlestick", "yAxis": 0, "color": 'blue'},
            {"name": "volume", "data": self.volume(), "type": "column", "yAxis": 1},
            {"name": "RSI", "data": self.RSI(period=14), "yAxis": 2},
            {"name": "macd_line", "data": self.macd_line(), "yAxis": 3},
            {"name": "macd_signal", "data": self.macd_signal(), "yAxis": 3},
            {"name": "%K", "data": self.stochastic_k(), "yAxis": 4},
            {"name": "%D", "data": self.stochastic_d(), "yAxis": 4},
            {"name": "%SD", "data": self.stochastic_sd(), "yAxis": 4},
        ]


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


def golden_cross(ins, format_string):
    v1 = getattr(ins, format_string % 1)
    v2 = getattr(ins, format_string % 2)
    return v1 > 0 and v2 < 0


def dead_cross(ins, format_string):
    v1 = getattr(ins, format_string % 1)
    v2 = getattr(ins, format_string % 2)
    return v1 < 0 and v2 > 0


buy_conditions = {
    "closing_rsi_14": lambda ins: ins.closing_rsi_14 <= 30,
    "closing_macd_minus_signal": lambda ins: golden_cross(ins, "closing_macd_minus_signal%s_26_12_9"),
    "ratio_closing_minus_rolling_mean_25": lambda ins: ins.ratio_closing_minus_rolling_mean_25 <= -10,
    "interval_closing_bollinger_band_20": lambda ins: ins.interval_closing_bollinger_band_20 <= -3,
}

sell_conditions = {
    "closing_rsi_14": lambda ins: ins.closing_rsi_14 >= 70,
    "closing_macd_minus_signal": lambda ins: dead_cross(ins, "closing_macd_minus_signal%s_26_12_9"),
    "ratio_closing_minus_rolling_mean_25": lambda ins: ins.ratio_closing_minus_rolling_mean_25 >= 10,
    "interval_closing_bollinger_band_20": lambda ins: ins.interval_closing_bollinger_band_20 >= 3,
}


class CompanySearchField(Wrapper):

    @property
    def number_of_signals(self):
        return len(self.signals)

    def signal(self, col_name):
        buy = buy_conditions[col_name]
        sell = sell_conditions[col_name]
        try:
            if buy(self.ins):
                return "BUY"
            elif sell(self.ins):
                return "SELL"
        except TypeError:
            pass
        return ""

    def signals(self):
        # TODO: implement
        s = {}
        for meth in dir(self):
            prefix = "signal_"
            if meth.startswith(prefix):
                s[meth[len(prefix):]] = getattr(self, meth)()
        return s


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
