# coding: utf-8
import sqlalchemy as sql

from stock import query
from stock import models

from logging import getLogger
logger = getLogger(__name__)


def get_scraper():
    from stock.scrape import YahooJapan
    return YahooJapan()


def session_each(iterable, add_instance, each=False, ignore=False):
    # TODO: use with statement
    session = query.session()
    for i in iterable:
        session.add(add_instance(**i))
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
    session.close()


def scrape_and_store_history(company, start=None, end=None, each=False, ignore=False):
    history = get_scraper().history(company.code, start, end)

    def add_instance(**kw):
        kw["company_id"] = company.id
        return models.DayInfo(**kw)

    session_each(history, add_instance)
