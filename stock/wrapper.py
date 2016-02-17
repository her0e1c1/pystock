import datetime

import sqlalchemy as sql
import pandas as pd


class Query(object):

    def __init__(self, q):
        self.q = q

    def __iter__(self):
        return iter(self.q)

    def __getattr__(self, name):
        attr = getattr(self.q, name)
        if callable(attr):
            def f(*args, **kw):
                r = attr(*args, **kw)
                if isinstance(r, sql.orm.query.Query):
                    return self.__class__(r)
                else:
                    return r
            return f
        else:
            return attr


class DayInfoQuery(Query):

    def to_series(self, type="closing"):
        return [(info.w.js_datetime, info.w.closing) for info in self]
        # df = pd.DataFrame([(info.w.js_datetime, info.w.closing) for info in self.q])
        # return pd.DataFrame([{"date": di.date, "closing": di.closing} for di in day_info_list])


class Wrapper(object):

    def __init__(self, ins):
        from . import models  # Not cyclic import
        assert isinstance(ins, getattr(models, self.__class__.__name__))
        self.ins = ins

    # company_idみたいに、定義されていない属性はinsから取得
    def __getattr__(self, name):
        return getattr(self.ins, name)

    def to_dict(self):
        assert getattr(self, "dict_keys", False), "Must need a dict_keys attribute"
        return {k: getattr(self, k) for k in self.dict_keys}


class Company(Wrapper):
    dict_keys = ["id", "name", "code"]

    def fix_data_frame(self):
        data_records = []
        for day_info in self.day_info_list:
            data = {
                "high": day_info.fix_high(),
                "low": day_info.fix_low(),
                "opening": day_info.fix_opening(),
                "closing": day_info.fix_closing(),
                "date":day_info.js_datetime}
            data_records.append(data)
        return pd.DataFrame.from_records(data_records)


class DayInfo(Wrapper):

    dict_keys = ["high", "low", "opening", "closing", "company_id", "js_datetime"]

    def __str__(self):
        return """\
cid  : {company_id}
open : {opening}
high : {high}
low  : {low}
close: {closing}
""".format(**self.to_dict())

    def _fix_value(self, value):
        for date in self.ins.company.split_stock_dates:
            if self.date < date.date:
                value *= date.from_number / float(date.to_number)
        return value

    @property
    def high(self):
        return self._fix_value(self.ins.high)

    @property
    def low(self):
        return self._fix_value(self.ins.low)

    @property
    def opening(self):
        return self._fix_value(self.ins.opening)

    @property
    def closing(self):
        return self._fix_value(self.ins.closing)

    @property
    def js_datetime(self):
        japan = self.ins.date + datetime.timedelta(hours=9)
        return int(japan.strftime("%s")) * 1000
