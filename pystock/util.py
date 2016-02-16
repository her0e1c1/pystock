import os
import time
import calendar
import datetime

from dateutil.relativedelta import relativedelta
import sqlalchemy as sql

from pystock import config as C


class DateRange(object):

    def __init__(self, start=None, end=None):
        if isinstance(end, str):
            end = str2date(start)
        if isinstance(start, str):
            start = str2date(start)
        if end is None:
            end = datetime.date.today()
        if start is None:
            start = end - relativedelta(days=C.DEFAULT_DAYS_PERIOD)
        self.end = end
        self.start = start

    def query(self, date_col):
        start, end = self.start, self.end
        if start is None:
            return date_col <= end
        elif end is None:
            return start <= date_col
        else:
            return sql.and_(start <= date_col, date_col <= end)

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


class Date(object):

    def __init__(self, year, month):
        self.first = datetime.date(year, month, 1)
        self.last = self.first + relativedelta(months=1, days=-1)

    def to_days(self):
        days = []
        if self.first < self.last:
            i = self.first
            while True:
                days.append(i)
                i += relativedelta(days=1)
                if i == self.last:
                    return days
        else:
            return []

    def __str__(self):
        return "from {first} to {last}".format(**self)


class DayInfoManager(object):

    def __init__(self, dayinfo_list):
        self.dayinfo_list = dayinfo_list

    def _sequence(self, key):
        for d in self.dayinfo_list:
            x = d.date
            y = getattr(d, key)
            yield (x, y)

    @property
    def sequence_high(self):
        return self._sequence("high")

    @property
    def sequence_low(self):
        return self._sequence("low")


def graph_month_dir(code, year, month, ext=".png"):
    name = C.FORMAT["month"].format(**locals())
    dir_ = C.FORMAT["image_dir"].format(code=code)
    if not os.path.isdir(dir_):
        os.makedirs(dir_)
    filepath = os.path.join(C.GRAPH_DIR, name + ext)
    return filepath


def last_day():
    """株の最後の日を返す"""
    today = datetime.date.today()
    weekday = today.weekday()
    if weekday in [calendar.SUNDAY, calendar.SATURDAY]:
        day = today + relativedelta.relativedelta(weekday=relativedelta.FR(-1))
    else:
        day = today - relativedelta(days=1)
    return day


def dict_inverse(dct):
    return {v: k for k, v in dct.items()}


def multiple_decorator(funcs):
    def wrap(g):
        for f in funcs:
            g = f(g)
    return wrap

def str2date(datestr):
    t = time.strptime(datestr, "%Y-%m-%d")
    return datetime.date.fromtimestamp(time.mktime(t))
