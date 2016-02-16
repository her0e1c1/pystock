import sqlalchemy as sql

from pystock import models

session = models.Session()


def get_info(code, start=None, end=None):
    return day_info_list


def store_day_info(company_id, day_info_list):
    """会社ごとに取得した毎日の株価のデータをデータベースに格納する
    """
    company = session.query(models.Company).filter_by(id=company_id).one()
    date_list = [d.date for d in company.day_info_list]
    for day_info in [d for d in day_info_list if d["date"] not in date_list]:
        d = {"company": company}
        d.update(day_info)
        if d["date"] in date_list:
            continue
        try:
            session.add(models.DayInfo(**d))
        except:
            # 型が混ざってる
            session.add(models.SplitStockDate(**d))

        try:
            session.commit()
        except sql.exc.IntegrityError:
            session.rollback()


def set_infos(start, end):
    for c in session.query(models.Company).all():
        set_info(c.code, start, end)


def set_info(code, start=None, end=None):
    company = get_company(code=code)
    day_info_list = get_info(code, start, end)
    store_day_info(company.id, day_info_list)
