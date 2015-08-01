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


def show(code, start, end=None, type="closing"):
    """指定された会社の株価を返す"""
    # TODO: 分割も考慮
    if end is None:
        end = datetime.date.today()

    start = str2date(start)
    end =  str2date(end)

    company = first_by(code=code, raise_error=True)

    day_infos = _get_day_info(company.id, start, end)

    # plt.plot(*result)
    return zip(*[(di.date, di.closing) for di in day_infos])
