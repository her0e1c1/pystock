# coding: utf-8
import pandas as pd

from stock import util

from . import company  # NOQA
from . import search_field  # NOQA
from . import table  # NOQA


def last_date():
    return util.last_date()


def make_data_frame(day_info_query):
    return pd.DataFrame(
        [(info.w.js_datetime, info.w.closing, info.w.volume,
            info.w.opening, info.w.high, info.w.low)
            for info in day_info_query],
        columns=["date", "closing", "volume", "opening", "high", "low"]
    )
