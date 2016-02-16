# -*- coding:utf-8 -*-
import datetime

import sqlalchemy as sql
import pandas as pd

from s import models


def first_by(code=None, raise_error=False):
    query = models.Session().query(models.Company)
    if code:
        query = query.filter_by(code=code)
    ins =  query.first()
    if not ins and raise_error:
        raise ValueError("not exists")
    return ins


def _get_day_info(company_id, start, end):
    di = models.DayInfo
    s = models.Session()
    query = s.query(di)
    query = query.filter_by(company_id=company_id)
    query = query.filter(sql.and_(
        start <= di.date
        #, di.date <= end
    ))
    return query.all()


def list_company_which_go_down_rolling_mean(period=90, type="closing"):
    """現在、長期移動平均線を下回っている会社を返す"""
    company_list = models.Session().query(models.Company).all()

    for company in company_list:
        df = company.fix_data_frame()
        if df is None:
            continue

        mean = pd.rolling_mean(df.closing, period)

        if (mean.tail(1) > df.closing.tail(1)).bool():
            yield company


def str2date(s):
    if isinstance(s, (str, unicode)):
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def convert_daterange(start, end):
    if end is None:
        end = datetime.date.today()

    start = str2date(start)
    end =  str2date(end)
    return start, end


def to_series(day_infos, type="closing"):
    # plt.plot(*result)
    return pd.DataFrame([{"date": di.date, "closing": di.closing} for di in day_infos])
    # return pd.DataFrame(zip(*[(di.date, di.closing) for di in day_infos]))


def show(code, start, end=None):
    """指定された会社の株価を返す"""
    # TODO: 分割も考慮
    start, end = convert_daterange(start, end)
    company = first_by(code=code, raise_error=True)
    day_infos = _get_day_info(company.id, start, end)
    return day_infos
    # return to_series(day_infos)


def show1(code, start, end=None):
    day_infos = show(code, start, end)
    df = to_series(day_infos)
    return df


def show_rolling_mean(code, start, end=None, type="closing", period=30):
    df = show1(code, start, end)
    mean = pd.rolling_mean(df.closing, period)
    return pd.DataFrame({"date": df.date, "rolling_mean": mean})
