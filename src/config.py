import os

HERE = os.path.dirname(__file__)

DEBUG = True

# URL = "mysql+mysqlconnector://root@localhost/stock?charset=utf8"
URL = "mysql+pymysql://root@localhost/stock?charset=utf8"
# URL = "sqlite:///:memory:"
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
