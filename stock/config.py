import os
import logging
from collections import OrderedDict


# Heroku can't import path (I don't know the reason)
# import path
# ROOTDIR = path.Path(__file__).parent.parent
ROOTDIR = "/".join(os.path.abspath(__file__).split("/")[:-2])

DEBUG = False
LOG_LEVEL = logging.INFO

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite://")
CREATE_ENGINE = {
    "encoding": 'utf-8',
    "pool_recycle": 3600,
    "echo": DEBUG,
}

SLACK_URL = os.environ.get("SLACK_URL")


# frequently changed
COMPANY_XLS_URL = "http://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
EXCEL_COMPANY_HEADER = OrderedDict([
    ("date", u'日付'),
    ("code", u'コード'),
    ("name", u'銘柄名'),
    ("_item", u'市場・商品区分'),
    ("category33", u'33業種コード'),
    ("label33", u'33業種区分'),
    ("category17", u'17業種コード'),
    ("label17", u'17業種区分'),
    ("scale", u'規模コード'),
    ("label_scale", u'規模区分'),
])
SHEET_NAME = "Sheet1"

# 今日から株価を取得する期間
DEFAULT_DAYS_PERIOD = 3 * 30


DEFAULT_ROLLING_MEAN_RATIO = 5


DATE_FORMATS = ["%Y/%m/%d", "%Y-%m-%d"]
