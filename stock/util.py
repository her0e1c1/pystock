import os
import io
import enum
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

logger = logging.getLogger(__name__)


def models_to_dataframe(alist, index=None):
    df = pd.DataFrame([a.__dict__ for a in alist])
    if index:
        return df.set_index(index)
    return df


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


def increment(x2, x1):
    if x2 is None or x1 is None:
        return None
    return float((x2 - x1) / x1) * 100


def increment_by(x1, v=1):
    if x1 is None:
        return None
    return x1 + (x1 * v) / 100.0


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


# VERY SLOW
def send_to_slack(text, channel="#pystock"):
    url = os.environ.get("SLACK_URL")
    if not url:
        logger.warn("NO SLACK URL")
        return
    logger.debug(text)
    if text.startswith("ERROR:"):
        channel = "#error"
    payload = {
        "text": text,
        "channel": channel
    }
    resp = requests.post(
        url,
        json.dumps(payload),
        headers={'content-type': 'application/json'}
    )
    if not resp.ok:
        logger.warn("SOMETHING WRONG ABOUT SLACK")


# don't use pandas to_json
def series_to_json(series):
    return list([a, b] for a, b in
                zip(series.index.values.tolist(), series.values.tolist())
                if not pd.isnull(b))


def schema(model, **kw):
    d = {k: getattr(model, k) for k in model.__table__.columns.keys()}
    for k, v in kw.items():
        d[k] = v
    return d


def schema_to_json(schema, o):
    if type(schema) == list:
        return [schema_to_json(schema[0], a) for a in o]
    elif type(schema) == dict:
        s = dict()
        for k, v in schema.items():
            v2 = o.get(k) if isinstance(o, dict) else getattr(o, k, None)
            s[k] = schema_to_json(v, v2)
        return s
    else:
        return o


def to_json(o):
    from . import models
    if isinstance(o, np.integer):
        return int(o)
    elif isinstance(o, np.floating):
        return float(o)
    elif isinstance(o, np.ndarray):
        return o.tolist()
    elif isinstance(o, (datetime.date, datetime.datetime)):
        return int(o.strftime("%s"))
    elif isinstance(o, pd.Series):
        return to_json(series_to_json(o))
    elif isinstance(o, pd.DataFrame):
        records = o.to_dict("records")
        for (i, index) in enumerate(o.index):
            records[i][o.index.name] = index
        return to_json(records)
    elif isinstance(o, dict):
        d = {}
        for k, v in o.items():
            d[k] = to_json(v)
        return d
    n = pd.isnull(o)
    if not hasattr(n, "all") and n:
        return None
    elif isinstance(o, enum.Enum):
        return o.value
    elif isinstance(o, list):
        return [to_json(x) for x in o]
    elif isinstance(o, models.Base):
        return {k: to_json(getattr(o, k)) for k in o.__table__.columns.keys()}
    return o


def json_dumps(o):
    return json.dumps(to_json(o))


def to_date(s=None, **kw):
    if not s:
        s = datetime.date.today()
    s = str2date(s)
    if kw:
        return s + relativedelta.relativedelta(**kw)
    return s


def str2date(s):
    # t = time.strptime(s, "%Y-%m-%d")
    # return datetime.date.fromtimestamp(time.mktime(t))
    if not s:
        return None
    if isinstance(s, (datetime.date, datetime.datetime)):
        return s
    if "/" in s:
        ss = s.split("/")
    elif "-" in s:
        ss = s.split("-")
    elif len(s) in [4, 6, 8]:  # YYYY, YYYYMM or YYYYMMDD
        ss = [s[: 4], s[4: 6], s[6: 8]]
        ss = [s for s in ss if s]
    else:
        return None
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
