import pandas as pd

from . import query


def make_data_frame(day_info_query):
    return pd.DataFrame(
        [(info.w.js_datetime, info.w.closing) for info in day_info_query],
        columns=["date", "closing"]
        )


def scrape_and_store(min_id=1, max_id=None, start=None, end=None,
                     each=False, ignore=False, last_date=None):
    if max_id is None:
        max_id = Company.max_id()
    for id in range(min_id, max_id + 1):
        set(id, each=each, ignore=True, last_date=last_date)


def get_companies(closing_minus_rolling_mean_25=None):
    session = query.models.Session()
    q = query.Company.query(session)
    if closing_minus_rolling_mean_25 is not None:
        q = q.join(query.models.Company.search_field)
        col = query.models.CompanySearchField.closing_minus_rolling_mean_25
        if closing_minus_rolling_mean_25 >= 0:
            q = q.filter(col >= closing_minus_rolling_mean_25)
        else:
            q = q.filter(col < closing_minus_rolling_mean_25)
    return q.all()


def closing_minus_rolling_mean_25(period=25):
    """長期移動平均線と現在の株価の差を予め計算"""
    session = query.models.Session()
    for company in query.Company.query(session):
        df = make_data_frame(query.DayInfo.get(company_id=company.id, session=session))
        mean = pd.rolling_mean(df.closing, period)
        diff = mean.tail(1) - df.closing.tail(1)
        if not diff.empty and int(diff):
            if company.search_field is None:
                sf = query.models.CompanySearchField()
            else:
                sf = company.search_field
            sf.closing_minus_rolling_mean_25 = int(diff)
            company.search_field = sf
            session.add(company)
    session.commit()
    session.close()
