from contextlib import contextmanager
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from . import config as C


engine = sql.create_engine(C.DATABASE_URL, **C.CREATE_ENGINE)
Base = declarative_base(bind=engine)
Session = sql.orm.sessionmaker(bind=engine)


def create_all():
    Base.metadata.create_all()


def drop_all():
    Base.metadata.drop_all()


# http://docs.sqlalchemy.org/en/rel_0_9/orm/session_basics.html#session-frequently-asked-questions
@contextmanager
def session_scope():
    s = Session()
    try:
        yield s
        s.commit()
    except Exception as e:
        print(e)  # for debug
        s.rollback()
    finally:
        s.close()


# Database code should be stored in key-value store
class QuandlCode(Base):

    __tablename__ = "quandl_code"

    code = sql.Column(sql.String(64), primary_key=True)  # TSE/1234
    database_code = sql.Column(sql.String(64))  # TSE

    @sql.orm.validates('code', 'database_code')
    def validate_code(self, _key, val):
        return val.upper()

    def __repr__(self):
        return "QuandlCode({code})".format(**self.__dict__)


@sql.event.listens_for(QuandlCode, 'before_insert')
def broker_before_insert(mapper, connection, qcode):
    splited = qcode.code.split("/", 2)
    if len(splited) == 2:
        db, _ = splited
        qcode.database_code = db


class Price(Base):  # Daily Price

    __tablename__ = "price"
    __table_args__ = (sql.UniqueConstraint('quandl_code', "date"),)

    high = sql.Column(sql.Float, nullable=True)
    low = sql.Column(sql.Float, nullable=True)
    open = sql.Column(sql.Float, nullable=True)
    close = sql.Column(sql.Float, nullable=True)
    date = sql.Column(sql.Date, nullable=False)
    quandl_code = sql.Column(sql.String(64), nullable=False)
    volume = sql.Column(sql.Integer, nullable=True)

    # FIXME: Remove ID
    id = sql.Column(sql.Integer, primary_key=True)

    @sql.orm.validates('quandl_code')
    def validate_quandl_code(self, _key, val):
        return val.upper()

    def __repr__(self):
        return f"Price({self.quandl_code}, {self.date})"


class CurrentPrice(Base):

    __tablename__ = "current_price"
    __table_args__ = (sql.UniqueConstraint('datetime', 'quandl_code'), )

    id = sql.Column(sql.Integer, primary_key=True)
    value = sql.Column(sql.Integer, nullable=False)
    datetime = sql.Column(sql.DateTime, nullable=False, index=True)
    quandl_code = sql.Column(sql.String(64), nullable=False, index=True)


# class SplitStockDate(Base):

#     __tablename__ = "split_stock_date"
#     __table_args__ = (sql.UniqueConstraint("date", "company_id"), )

#     from_number = sql.Column(sql.Integer, nullable=False)
#     to_number = sql.Column(sql.Integer, nullable=False)
#     date = sql.Column(sql.Date, nullable=False)
#     quandl_code = sql.Column(sql.String(64), nullable=False, index=True)
