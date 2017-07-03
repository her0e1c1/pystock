import io
import zipfile
import csv
import json
import calendar
import datetime
import logging

import numpy as np
import pandas as pd
import requests
from dateutil import relativedelta

from . import config as C

logger = logging.getLogger(__name__)


# TODO: 呼び出し側でのNoneの考慮 + float()でwrapする?, invaid=Trueつける?
def last(series, offset_from_last=0):
    return _last(series, offset_from_last)


def _last(series, offset_from_last=0):
    if offset_from_last == 0:
        return series[-1]
    elif offset_from_last > 0:
        return series[-(offset_from_last + 1)]
    i = series.last_valid_index()  # .tail(1)使える?
    if i is None:  # or pd.isnull(i)
        return
    elif offset_from_last == 0:
        return series[i]
    elif i - offset_from_last >= 0:  # if index is datetime, then an error
        return series[i - offset_from_last]


def increment(a, b):
    if a is None or b is None:
        return None
    return float((a - b) / b) * 100


def sigma(series, period):
    """
    [-4, 4] or Noneを返す。
    つまり、
    現在値と平均が同じ => 0
    (0, 1] => 1
    (1, 2] => 2
    (2, 3] => 3
    (4,  ] => 4 (4sigma以上)
    また、負の方向はマイナスをつけるだけ
    """
    if series.empty:  # 他の関数にも書いたほうがいいかも(呼び出し側で気をつける?)
        return
    rolling = series.rolling(window=period, center=False)
    mean = last(rolling.mean())
    std = last(rolling.std())
    curr = last(series)
    if any([x is None for x in [curr, mean, std]]):
        return
    if curr == mean:
        return 0
    sign = 1 if curr > mean else -1
    for sigma in [1, 2, 3]:
        m1 = mean + sign * std * (sigma - 1)
        m2 = mean + sign * std * sigma
        if min(m1, m2) < curr <= max(m1, m2):  # fix import
            return sign * sigma
    else:
        return 4 * sign


# Return "BUY", "SELL", NONE
def cross(fast, slow):
    """
    golden cross: 短期が長期を下から上に抜けた場合(BUY)
    dead cross  : 短期が長期を上から下に抜けた場合(SELL)
    """
    f0 = last(fast)
    f1 = last(fast, offset_from_last=1)
    s0 = last(slow)
    s1 = last(slow, offset_from_last=1)
    if any([x is None for x in [f0, f1, s0, s1]]):
        return
    d0 = float(f0 - s0)
    d1 = float(f1 - s1)
    if d1 < 0 and d0 > 0:
        return "BUY"
    elif d1 > 0 and d0 < 0:
        return "SELL"




def send_to_slack(text, channel="#pystock"):
    if not C.SLACK_URL:
        logger.warn("NO SLACK URL")
        return
    logger.debug(text)
    payload = {
        "text": text,
        "channel": channel
    }
    resp = requests.post(
        C.SLACK_URL,
        json.dumps(payload),
        headers={'content-type': 'application/json'}
    )
    if not resp.ok:
        logger.warn("SOMETHING WRONG ABOUT SLACK")


# type = [candlestick, column]
def series_to_json(series):
    # WARN: nan can not JSON Serializable
    def to_sec(x):  # date convertor
        if isinstance(x, (datetime.date, datetime.datetime)):
            return int(x.strftime("%s"))
        return x
    return list([to_sec(a), to_sec(b)] for a, b in
                zip(series.index.values.tolist(), series.values.tolist())
                if not pd.isnull(b))


class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, np.integer):
            return int(o)
        elif pd.isnull(o):
            return None
        elif isinstance(o, np.floating):
            return float(o)
        elif isinstance(o, np.ndarray):
            return o.tolist()
        elif isinstance(o, (datetime.date, datetime.datetime)):
            return int(o.strftime("%s"))
        else:
            return super(JsonEncoder, self).default(o)


# don't use pandas to_json
def to_json(o):
    if isinstance(o, dict):
        d = {}
        for k, v in o.items():
            d[k] = to_json(v)
        return d
    elif isinstance(o, list):
        return [to_json(x) for x in o]
    elif isinstance(o, pd.Series):
        return to_json(series_to_json(o))  # key is `o.name`
    elif isinstance(o, pd.DataFrame):
        d = {}
        for k, v in o.items():
            d[k] = to_json(v)
        return d
    if pd.isnull(o):  # HOTFIX
        return None
    return o


def json_dumps(o):
    return json.dumps(to_json(o), cls=JsonEncoder)


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
