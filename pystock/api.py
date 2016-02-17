# -*- coding:utf-8 -*-
import datetime

import sqlalchemy as sql
import pandas as pd

from s import models


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


def show_rolling_mean(code, start, end=None, type="closing", period=30):
    df = show1(code, start, end)
    mean = pd.rolling_mean(df.closing, period)
    return pd.DataFrame({"date": df.date, "rolling_mean": mean})
