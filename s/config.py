# coding: utf-8
import os
from collections import OrderedDict

HERE = os.path.dirname(__file__)

DEBUG = False
# DEBUG = True

URL = "mysql+pymysql://root@localhost/stock?charset=utf8"
# URL = "sqlite:///:memory:"
# URL = "mysql+mysqlconnector://root@localhost/stock?charset=utf8"

# sqlalchemy
CREATE_ENGINE = {
    "encoding": 'utf-8',
    "echo": DEBUG,
}

STATIC_DIR = os.path.join(HERE, "static")

GRAPH_DIR = os.path.join(STATIC_DIR, "company")

FORMAT = {
    "image_dir": os.path.join(GRAPH_DIR, "{code}"),
    "month": "{code}/{year}_{month}",
}

EXCEL_COMPANY_HEADER = OrderedDict([
    ("date", u'日付'),
    ("code", u'コード'),
    ("name", u'銘柄名'),
    ("category33", u'33業種コード'),
    ("label33", u'33業種区分'),
    ("category17", u'17業種コード'),
    ("label17", u'17業種区分'),
    ("scale", u'規模コード'),
    ("label_scale", u'規模区分'),
])
SHEET_NAME = "Sheet1"
