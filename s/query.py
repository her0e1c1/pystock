
import datetime

from s import models
from s import util


class Query(object):
    model = None

    @classmethod
    def session(cls):
        return models.Session()

    @classmethod
    def query(cls):
        return cls.session().query(cls.model)

    @classmethod
    def one(cls, id):
        return cls.query().filter_by(id=id).one()


class DayInfo(Query):
    model = models.DayInfo

    @classmethod
    def get(cls, company_id, start=None, end=None):
        q = cls.query().filter_by(company_id=company_id)
        q = q.filter(util.DateRange(start, end).query(cls.model.date))
        q = q.order_by("date")
        return q


class Company(Query):
    model = models.Company

    @classmethod
    def is_updated(cls, id):
        """会社の最新情報に更新されていればTrue"""
        last = util.last_day()
        q = cls.query()
        q = q.filter_by(id=id)
        return q.count() > 0


# TODO: 指定した日付の価格を取得
def update_per_day(date=None):
    if date is None:
        date = datetime.date.today()
