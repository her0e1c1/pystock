# -*- coding:utf-8 -*-

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
