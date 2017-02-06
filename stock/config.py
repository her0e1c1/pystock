# coding: utf-8
import os
import logging
from collections import OrderedDict


def set(**kw):
    g = globals()
    for k, v in kw.items():
        g[k.upper()] = v  # raise KeyError if the key does not exist


# Heroku can't import path (I don't know the reason)
# import path
# ROOTDIR = path.Path(__file__).parent.parent
ROOTDIR = "/".join(os.path.abspath(__file__).split("/")[:-2])

HERE = os.path.dirname(__file__)

DEBUG = False
LOG_LEVEL = logging.INFO

HOST = "localhost"
PORT = int(os.environ.get('PORT', 5000))

# sqlalchemy
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///%s/db.sqlite3" % HERE)
CREATE_ENGINE = {
    "encoding": 'utf-8',
    "pool_recycle": 3600,
    "echo": DEBUG,
}

QUANDL_CODE_API_KEY = os.environ.get("QUANDL_CODE_API_KEY")

STATIC_DIR = os.path.join(ROOTDIR, "static")

GRAPH_DIR = os.path.join(STATIC_DIR, "company")

FORMAT = {
    "image_dir": os.path.join(GRAPH_DIR, "{code}"),
    "month": "{code}/{year}_{month}",
}


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


MAP_PRICE_COLUMNS = {}
for v in ["open", "close", "high", "low"]:
    p = "price"
    keys = [v, v.title(), "%s %s" % (v, p), "%s %s" % (v.title(), p.title()), "%s%s" % (v.title(), p.title())]
    for k in keys:
        MAP_PRICE_COLUMNS[k] = v
