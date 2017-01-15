# coding: utf-8
import calendar
import datetime

from dateutil import relativedelta


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


def js_datetime(date):
    japan = date + datetime.timedelta(hours=9)
    return int(japan.strftime("%s")) * 1000
