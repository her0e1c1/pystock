# coding: utf-8
from logging import getLogger

import sqlalchemy as sql

from . import models
from . import util

logger = getLogger(__name__)


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
    def get(cls, company_id, start=None, end=None, session=None):
        q = cls.query(session).filter_by(company_id=company_id)
        q = q.filter(util.DateRange(start, end).query(cls.model.date))
        q = q.order_by("date")
        return q


class Company(Query):
    model = models.Company

    @classmethod
    def all(cls, session=None, last_date=None, limit=None, **kw):
        q = cls.query(session).filter_by(**kw)
        if limit:
            q = q.limit(limit)
        if last_date:
            q = q.filter(sql.not_(models.Company.day_info_list.any(date=last_date)))
        return q.all()

    @classmethod
    def first(cls, session=None, last_date=None, **kw):
        q = cls.query(session).filter_by(**kw)
        if last_date:
            q = q.filter(sql.not_(models.Company.day_info_list.any(date=last_date)))
        return q.first()

    @classmethod
    def max_id(cls):
        q = cls.query()
        q = q.order_by("-id")
        c = q.first()
        return c.id if c else 0
