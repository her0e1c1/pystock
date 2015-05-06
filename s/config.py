import os
from collections import OrderedDict

HERE = os.path.dirname(__file__)

DEBUG = True

URL = "mysql+pymysql://root@localhost/stock"
# URL = "sqlite:///:memory:"
# URL = "mysql+mysqlconnector://root@localhost/stock?charset=utf8"

CREATE_ENGINE = {
    "encoding": 'utf-8',
    "echo": True,
}
STATIC_DIR = os.path.join(HERE, "static")

GRAPH_DIR = os.path.join(STATIC_DIR, "company")
FORMAT = {
    "image_dir": os.path.join(GRAPH_DIR, "{code}"),
    "month": "{code}/{year}_{month}",
}

EXCEL_COMPANY_HEADER = OrderedDict([
    ("date", '日付'),
    ("code", 'コード'),
    ("name", '銘柄名'),
    ("category33", '33業種コード'),
    ("label33", '33業種区分'),
    ("category17", '17業種コード'),
    ("label17", '17業種区分'),
    ("scale", '規模コード'),
    ("label_scale", '規模区分'),
])
