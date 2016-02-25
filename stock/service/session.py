from stock import query


def with_session(f, col_name, session=None):
    from stock.service import make_data_frame
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
