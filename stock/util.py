import io
import zipfile
import csv
import json
import time
import calendar
import datetime

import pandas as pd
from dateutil import relativedelta

from . import config as C


# for front end
def to_ja(date):
    japan = date + datetime.timedelta(hours=9)
    return int(japan.strftime("%s")) * 1000


# type = [candlestick, column]
def series_to_json(series, japan=True):
    # WARN: nan can not JSON Serializable
    return list([to_ja(a), b] for a, b in zip(series.index.values.tolist(), series.values.tolist())
                if not pd.isnull(b))


# don't use pandas to_json
def to_json(o):
    if isinstance(o, pd.Series):
        return to_json(series_to_json(o))  # key is `o.name`
    elif isinstance(o, pd.DataFrame):
        d = {}
        # NOTE: val is a list of numpy.int64 (Not JSON serializable)
        for key, val in o.items():
            d[key] = series_to_json(val)
            return to_json(d)
    return o


def json_dumps(o):
    return json.dumps(to_json(o))


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


def str2date(s):
    # t = time.strptime(s, "%Y-%m-%d")
    # return datetime.date.fromtimestamp(time.mktime(t))
    if not s:
        raise ValueError("Invaid Format")
    if "/" in s:
        ss = s.split("/")
    elif "-" in s:
        ss = s.split("-")
    elif len(s) in [4, 6]:  # YYYYMM or YYYYMMDD
        ss = [s[: 4], s[4: 6], s[6: 8]]
        ss = [s for s in ss if s]
    else:
        raise ValueError("Invaid Format")
    if len(ss) == 1:
        return datetime.date(int(ss[0]), 1, 1)
    elif len(ss) == 2:
        return datetime.date(int(ss[0]), int(ss[1]), 1)
    else:
        return datetime.date(int(ss[0]), int(ss[1]), int(ss[2]))


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


def last_date():
    """株の最後の日を返す"""
    # for JST
    now = datetime.datetime.today() + relativedelta.relativedelta(hours=9)
    weekday = now.weekday()
    if weekday in [calendar.SUNDAY, calendar.SATURDAY]:
        dt = now + relativedelta.relativedelta(weekday=relativedelta.FR(-1))
    else:
        dt = now - relativedelta.relativedelta(days=1)
    return dt.date()


def fix_value(value, split_stock_dates, today=None):
    """
    Need to convert by split stock dates
    """
    for date in split_stock_dates:
        if today < date.date:
            value *= date.from_number / float(date.to_number)
    return value
