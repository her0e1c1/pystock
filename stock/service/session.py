# coding: utf-8
import sqlalchemy as sql

from stock import query


class Session(object):

    def __init__(self, ignore=False, each=False):
        self._s = query.models.Session()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def commit(self):
        self._s.commit()

    def close(self):
        self._s.close()

    def each(self, iterable, add_instance):
        for i in iterable:
            self._s.add(add_instance(**i))
            if not self.each:
                continue
            try:
                self.commit()
            except sql.exc.IntegrityError:
                self._s.rollback()
        if not self.each:
            try:
                self.commit()
            except sql.exc.IntegrityError as e:
                if not self.gnore:
                    raise e

    def with_session(self, f, col_name):
        from stock.service.day_info import make_data_frame
        session = self._s
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
