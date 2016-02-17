import datetime

import sqlalchemy as sql

from . import models
from . import util
from . import wrapper


class Query(object):
    model = None

    @classmethod
    def session(cls):
        return models.Session()

    @classmethod
    def query(cls, session=None):
        if session is None:
            session = cls.session()
        return session.query(cls.model)

    @classmethod
    def one(cls, id, session=None):
        return cls.query(session).filter_by(id=id).one()

    @classmethod
    def first(cls, session=None, **kw):
        return cls.query(session).filter_by(**kw).first()


class DayInfo(Query):
    model = models.DayInfo

    @classmethod
    def get(cls, company_id, start=None, end=None):
        q = cls.query().filter_by(company_id=company_id)
        q = wrapper.DayInfoQuery(q)
        q = q.filter(util.DateRange(start, end).query(cls.model.date))
        q = q.order_by("date")
        return q

    @classmethod
    def set(cls, company_id, start=None, end=None, each=False, ignore=False, last_date=None):
        from pystock.scrape import YahooJapan
        session = cls.session()
        scraper = YahooJapan()
        c = Company.first(company_id, last_date=last_date, session=session)
        if not c:
            return  # skip
        history = scraper.history(c.code, start, end)
        for d in history:
            d["company_id"] = company_id
            session.add(models.DayInfo(**d))
            if not each:
                continue
            try:
                session.commit()
            except sql.exc.IntegrityError:
                session.rollback()
        if not each:
            try:
                session.commit()
            except sql.exc.IntegrityError as e:
                if not ignore:
                    raise e


class Company(Query):
    model = models.Company

    @classmethod
    def first(cls, session=None, last_date=None, **kw):
        q = cls.query(session).filter_by(**kw)
        return q.first()

    @classmethod
    def max_id(cls):
        q = cls.query()
        q = q.order_by("-id")
        c = q.first()
        return c.id if c else 0

    @classmethod
    def is_updated(cls, id):
        """会社の最新情報に更新されていればTrue"""
        last = util.last_day()
        q = cls.query()
        q = q.filter_by(id=id)
        return q.count() > 0


def go_down_rolling_mean():
    """長期移動平均線を下回っている株を表示する
    """
    low_cost_company_list = []
    for c in session.query(models.Company).all():
        df = c.fix_data_frame()
        mean = pd.rolling_mean(df.closing, 90)

        cmp = mean.tail(1) > df.closing.tail(1)
        if cmp.bool():
            low_cost_company_list.append(c)
    return low_cost_company_list

