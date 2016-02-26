# coding: utf-8
import os
import path
import logging
from collections import OrderedDict


def set(**kw):
    g = globals()
    for k, v in kw.items():
        g[k.upper()] = v  # raise KeyError if the key does not exist


ROOTDIR = path.Path(__file__).parent.parent
HERE = os.path.dirname(__file__)

DEBUG = False
LOG_LEVEL = logging.INFO

PORT = int(os.environ.get('PORT', 5000))

# sqlalchemy
# DEFAULT_URL = "sqlite:///:memory:"
DEFAULT_URL = "mysql+pymysql://root@localhost/stock?charset=utf8"
URL = os.environ.get("DATABASE_URL", DEFAULT_URL)
CREATE_ENGINE = {
    "encoding": 'utf-8',
    "echo": DEBUG,
}

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

# Stock links
STOCK_LINKS = [
    # screening
    "http://www.traders.co.jp/domestic_stocks/invest_tool/screening/screening_top.asp",
    "http://jp.kabumap.com/servlets/kabumap/Action?SRC=navList/base&cid=find",
    "http://www.rizumu.net/search/",
    "http://minkabu.jp/screening",
    "http://kabusensor.com/screening/",
    "http://www.dreamvisor.com/quote_search_menu.cgi",
    "http://www.marble-cafe.com/alpha/cgi/screening/sacs.cgi",
    "http://www.stockweather.co.jp/sw2/screening.aspx",

    # Others
    "http://www.sevendata.co.jp/",
    "http://chartnavi.com/",
]
