import enum
import datetime
from contextlib import contextmanager
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from . import config as C


class Signal(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


engine = sql.create_engine(C.DATABASE_URL, **C.CREATE_ENGINE)
Base = declarative_base(bind=engine)
Session = sql.orm.sessionmaker(bind=engine)


def create_all():
    Base.metadata.create_all()


def drop_all():
    Base.metadata.drop_all()


# http://docs.sqlalchemy.org/en/rel_0_9/orm/session_basics.html#session-frequently-asked-questions
@contextmanager
def session_scope(**kw):
    s = Session(**kw)
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


class Price(Base):  # Daily Price

    __tablename__ = "price"
    __table_args__ = (sql.UniqueConstraint('quandl_code', "date"),)

    id = sql.Column(sql.Integer, primary_key=True)
    high = sql.Column(sql.Float, nullable=True)
    low = sql.Column(sql.Float, nullable=True)
    open = sql.Column(sql.Float, nullable=True)
    close = sql.Column(sql.Float, nullable=True)
    date = sql.Column(sql.Date, nullable=False)
    volume = sql.Column(sql.Integer, nullable=True)
    quandl_code = sql.Column(sql.String(64), sql.ForeignKey('quandl_code.code', ondelete='CASCADE', onupdate='NO ACTION'), nullable=False)

    code = sql.orm.relation("QuandlCode", backref="prices")

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


class Signal(Base):

    __tablename__ = "signal"

    # one to one
    quandl_code = sql.Column(sql.String(64), sql.ForeignKey('quandl_code.code', ondelete='CASCADE', onupdate='NO ACTION'), nullable=False, primary_key=True)
    updated_at = sql.Column(sql.DateTime, onupdate=datetime.datetime.utcnow, default=datetime.datetime.utcnow, nullable=False)
    created_at = sql.Column(sql.DateTime, default=datetime.datetime.utcnow, nullable=False)

    # expect index merge on mysql :D
    macd_signal = sql.Column(sql.Enum(Signal), index=True)
    rsi = sql.Column(sql.Enum(Signal), index=True)
    stochastic = sql.Column(sql.Enum(Signal), index=True)
    bollinger_band = sql.Column(sql.Enum(Signal), index=True)
    rolling_mean = sql.Column(sql.Enum(Signal), index=True)

    # cache
    price_id = sql.Column(sql.Integer, sql.ForeignKey('price.id', ondelete='CASCADE', onupdate='NO ACTION'))

    code = sql.orm.relation("QuandlCode", backref=(sql.orm.backref("signal", uselist=False)))
    price = sql.orm.relation("Price")


@sql.event.listens_for(QuandlCode, 'before_insert')
def code_before_insert(mapper, connection, qcode):
    s = sql.inspect(qcode).session
    splited = qcode.code.split("/", 2)
    if len(splited) == 2:
        db, _ = splited
        qcode.database_code = db

        # before_insert is called after before_flush and before_commit :(
        @sql.event.listens_for(s, 'after_flush', once=True)
        def f(session, flush_context):
            qcode.signal = Signal()


# Not to fire ORM events but insert is very slow :(
# data.to_sql("price", models.engine, if_exists='append')  # auto commit
# @sql.event.listens_for(Price, 'before_insert')
# def price_before_insert(mapper, connection, price):
#     s = sql.inspect(price).session
#     if not (price.code and price.code.signal):  # FXIME: N+1
#         signal = s.query(Signal).filter_by(quandl_code=price.quandl_code).one()
#     else:
#         signal = price.code.signal
#     latest = signal.price
#     with s.begin_nested() as st:
#         if not latest or latest.date < price.date:
#             sql.orm.attributes.set_committed_value(signal, "price", price)


# class SplitStockDate(Base):

#     __tablename__ = "split_stock_date"
#     __table_args__ = (sql.UniqueConstraint("date", "company_id"), )

#     from_number = sql.Column(sql.Integer, nullable=False)
#     to_number = sql.Column(sql.Integer, nullable=False)
#     date = sql.Column(sql.Date, nullable=False)
#     quandl_code = sql.Column(sql.String(64), nullable=False, index=True)
