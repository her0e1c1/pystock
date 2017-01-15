# coding: utf-8
import io
import zipfile
import csv
import time
import datetime

import pandas as pd
from dateutil import relativedelta

from . import config as C


def to_ja(date):
    japan = date + datetime.timedelta(hours=9)
    return int(japan.strftime("%s")) * 1000


# type = [candlestick, column]
def series_to_json(series, japan=True):
    # WARN: nan can not JSON Serializable
    return list([to_ja(a), b] for a, b in zip(series.index.values.tolist(), series.values.tolist())
                if not pd.isnull(b))


def df_to_series(df, color=None, type=None):
    series = []
    if isinstance(df, pd.core.series.Series):
        return [{"name": df.name, "data": series_to_json(df)}]
    for index, (name, data) in enumerate(df_to_json(df).items()):
        series.append({
            "name": name,
            "data": data,
            # "yAxis": index,
        })
    return series

    # {title: {text: 'OHLC'}, height: '60%'},
    # {title: {text: 'Volume'}, height: '10%', top: '60%'},
    # {title: {text: 'RSI'}, height: '10%', top: '80%'},
    # {title: {text: 'MACD'}, height: '10%', top: '90%'},
    # {title: {text: 'stochastic'}, height: '10%', top: '70%'},


def df_to_json(df):
    d = {}
    # NOTE: val is a list of numpy.int64 (Not JSON serializable)
    for key, val in df.items():
        d[key] = series_to_json(val)
    return d


class DateRange(object):

    def __init__(self, start=None, end=None):
        if isinstance(end, str):
            end = str2date(start)
        if isinstance(start, str):
            start = str2date(start)
        if end is None:
            end = datetime.date.today()
        if start is None:
            start = end - relativedelta.relativedelta(days=C.DEFAULT_DAYS_PERIOD)
        self.end = end
        self.start = start

    # def query(self, date_col):
    #     start, end = self.start, self.end
    #     if start is None:
    #         return date_col <= end
    #     elif end is None:
    #         return start <= date_col
    #     else:
    #         import sqlalchemy as sql
    #         return sql.and_(start <= date_col, date_col <= end)

    def to_dict(self):
        return {"start": str(self.start), "end": str(self.end)}

    def to_short_dict(self):
        return {
            "sy": self.start.year,
            "sm": self.start.month,
            "sd": self.start.day,
            "ey": self.end.year,
            "em": self.end.month,
            "ed": self.end.day,
        }


def dict_inverse(dct):
    return {v: k for k, v in dct.items()}


def str2date(datestr):
    if datestr:
        t = time.strptime(datestr, "%Y-%m-%d")
        return datetime.date.fromtimestamp(time.mktime(t))


def str_to_date(s):
    import datetime
    for fmt in C.DATE_FORMATS:
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except:
            pass
    else:
        raise ValueError


def read_csv_zip(fn, content):
    ls = []
    with zipfile.ZipFile(io.BytesIO(content)) as fh:
        for f in fh.infolist():
            csv_fh = io.StringIO(fh.open(f.filename).read().decode())
            for row in csv.reader(csv_fh):
                ls.append(fn(row))
    return ls
