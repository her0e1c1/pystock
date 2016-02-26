# coding: utf-8
import sqlalchemy as sql

from stock import query


def with_session(f, col_name, session=None):
    from stock.service.day_info import make_data_frame
    session = session or query.models.Session()
    for c in query.Company.query(session):
        df = make_data_frame(query.DayInfo.get(company_id=c.id, session=session))
        value = f(df)
        if value is None:
            continue
        if c.search_field is None:
            sf = query.models.CompanySearchField()
        else:
            sf = c.search_field
        setattr(sf, col_name, value)
        c.search_field = sf
        session.add(c)
    session.commit()
    session.close()


def session_each(iterable, add_instance, each=False, ignore=False, session=None):
    # TODO: use with statement
    close = False
    if session is None:
        session = query.session()
        close = True
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
    if close:
        session.close()
