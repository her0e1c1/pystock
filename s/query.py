from s import models
from s import util


def get_company_info(company_id, start=None, end=None):
    d = models.DayInfo
    session = models.Session()
    q = session.query(d).filter_by(company_id=company_id)
    q = q.filter(util.DateRange(start, end).query(d.date))
    q = q.order_by("date")
    return q
