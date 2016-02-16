import datetime
import sqlalchemy as sql

from . import scrape_stocks
from pystock import models
from pystock import config as C

session = models.Session()


def get_info(code, start=None, end=None):
    """期間を指定して企業の株を取得する"""
    if end is None:
        end = datetime.date.today()

    if start is None:
        start = end - datetime.timedelta(days=C.DEFAULT_DAYS_PERIOD)

    yahoo = scrape_stocks.HistoryYahooJapanFinance()
    day_info_list = yahoo.history(code, start.year, start.month, start.day,
                                        end.year, end.month, end.day)
    return day_info_list


def get_company_info(id):
    company = session.query(models.Company).filter_by(id=id).one()
    date_list = [d.date for d in company.day_info_list]
    day = last_day()
    if day in date_list:
        return
    try:
        info = get_info(company.code)
    except:
        return

    for day_info in info:
        d = {"company": company}
        d.update(day_info)
        if d["date"] in date_list:
            continue
        try:
            session.add(models.DayInfo(**d))
        except:
            session.add(models.SplitStockDate(**d))

        try:
            session.commit()
        except sql.exc.IntegrityError:
            session.rollback()


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


def set_infos(start, end):
    for c in session.query(models.Company).all():
        set_info(c.code, start, end)


def set_info(code, start=None, end=None):
    company = get_company(code=code)
    day_info_list = get_info(code, start, end)
    store_day_info(company.id, day_info_list)


def get_company(code=None):
    if code:
        return session.query(models.Company).filter_by(code=code).one()
    raise ValueError("There are no companies.")
