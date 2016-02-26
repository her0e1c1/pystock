# coding: utf-8
import time
import datetime

import sqlalchemy as sql
from dateutil import relativedelta

from . import config as C


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


def dict_inverse(dct):
    return {v: k for k, v in dct.items()}


def str2date(datestr):
    if datestr:
        t = time.strptime(datestr, "%Y-%m-%d")
        return datetime.date.fromtimestamp(time.mktime(t))
