
DEBUG = True

# URL = "mysql+mysqlconnector://root@localhost/stock?charset=utf8"
URL = "mysql+pymysql://root@localhost/stock?charset=utf8"
# URL = "sqlite:///:memory:"
CREATE_ENGINE = {
    "encoding": 'utf-8',
    "echo": True,
}
