# coding: utf-8
import os
import path
from collections import OrderedDict

ROOTDIR = path.Path(__file__).parent.parent
HERE = os.path.dirname(__file__)

DEBUG = True

PORT = int(os.environ.get('PORT', 5000))

# URL = "sqlite:///:memory:"
# URL = "mysql+mysqlconnector://root@localhost/stock?charset=utf8"
DEFAULT_URL = "mysql+pymysql://root@localhost/stock?charset=utf8"
URL = os.environ.get("DATABASE_URL", DEFAULT_URL)

# sqlalchemy
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
