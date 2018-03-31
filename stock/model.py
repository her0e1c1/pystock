import os
import sys
import inspect
import enum
import datetime
from contextlib import contextmanager
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from stock import util


class Signal(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


engine = sql.create_engine(
    os.environ.get("DATABASE_URL", "sqlite://"),
    **{
        "encoding": 'utf-8',
        "pool_recycle": 3600,
        "echo": bool(os.environ.get("DEBUG", False)),
    }
)
Base = declarative_base(bind=engine)
Session = sql.orm.sessionmaker(bind=engine)


def create_all():
    Base.metadata.create_all()


def drop_all():
    Base.metadata.drop_all()


def is_sqlite():
    return engine.url.drivername == "sqlite"


# http://docs.sqlalchemy.org/en/rel_0_9/orm/session_basics.html#session-frequently-asked-questions
@contextmanager
def session_scope(**kw):
    s = Session(**kw)
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()


def key_to_column(key):
    splited = key.split(".", 1)
    table, col = "", ""
    if len(splited) == 2:
        table, col = splited
    else:
        col = splited[0]
    models = inspect.getmembers(sys.modules[__name__], lambda x: inspect.isclass(x) and issubclass(x, Base))
    for _, m in models:
        if not hasattr(m, "__tablename__"):
            continue
        if table and not m.__tablename__.startswith(table):
            continue
        for name, column in m.__table__.columns.items():
            if name.startswith(col):
                return column


# Database code should be stored in key-value store
class Code(Base):

    __tablename__ = "code"

    id = sql.Column(sql.String(64), primary_key=True)  # TSE/1234
    database = sql.Column(sql.String(64))  # TSE

    @sql.orm.validates('code', 'database')
    def validate_code(self, _key, val):
        return val.upper()

    def __repr__(self):
        return "Code({id})".format(**self.__dict__)


class DailyPrice(Base):

    __tablename__ = "daily_price"
    __table_args__ = (sql.PrimaryKeyConstraint('code_id', "date"), )

    high = sql.Column(sql.Float, nullable=True)
    low = sql.Column(sql.Float, nullable=True)
    open = sql.Column(sql.Float, nullable=True)
    close = sql.Column(sql.Float, nullable=True)
    date = sql.Column(sql.Date, nullable=False)
    volume = sql.Column(sql.Integer, nullable=True)
    code_id = sql.Column(
        sql.String(64),
        sql.ForeignKey(
            'code.id',
            ondelete='CASCADE',
            onupdate='NO ACTION'
        ),
        nullable=False
    )

    code = sql.orm.relation("Code", backref="prices")

    @sql.orm.validates('code')
    def validate_code(self, _key, val):
        return val.upper()

    def __repr__(self):
        return f"Price({self.code_id}, {self.date})"


class CurrentPrice(Base):

    __tablename__ = "current_price"
    __table_args__ = (sql.PrimaryKeyConstraint('code_id', 'datetime'), )

    datetime = sql.Column(sql.DateTime, nullable=False)
    value = sql.Column(sql.Integer, nullable=False)
    code_id = sql.Column(
        sql.String(64),
        sql.ForeignKey(
            'code.id',
            ondelete='CASCADE',
            onupdate='NO ACTION'
        ),
        nullable=False
    )


class Signal(Base):

    __tablename__ = "signal"

    # one to one
    code_id = sql.Column(sql.String(64), sql.ForeignKey('code.id', ondelete='CASCADE', onupdate='NO ACTION'), nullable=False, primary_key=True)
    updated_at = sql.Column(sql.DateTime, onupdate=datetime.datetime.utcnow, default=datetime.datetime.utcnow, nullable=False)
    created_at = sql.Column(sql.DateTime, default=datetime.datetime.utcnow, nullable=False)

    # expect index merge on mysql :D
    macd_signal = sql.Column(sql.Enum(Signal), index=True)
    rsi = sql.Column(sql.Enum(Signal), index=True)
    stochastic = sql.Column(sql.Enum(Signal), index=True)
    bollinger_band = sql.Column(sql.Enum(Signal), index=True)
    rolling_mean = sql.Column(sql.Enum(Signal), index=True)

    # cache
    daily_price_date = sql.Column(sql.Integer, sql.ForeignKey('daily_price.date', ondelete='CASCADE', onupdate='NO ACTION'))
    prev_daily_price_date = sql.Column(sql.Integer, sql.ForeignKey('daily_price.date', ondelete='CASCADE', onupdate='NO ACTION'))
    change = sql.Column(sql.Float, index=True)
    change_percent = sql.Column(sql.Float, index=True)

    # prediction
    buying_price = sql.Column(sql.Float, index=True)
    buying_price_2 = sql.Column(sql.Float, index=True)
    buying_price_3 = sql.Column(sql.Float, index=True)

    # last value of a line (for now 25 days)
    historical_volatility = sql.Column(sql.Float, index=True)
    std = sql.Column(sql.Float, index=True)
    var = sql.Column(sql.Float, index=True)
    mean = sql.Column(sql.Float, index=True)

    code = sql.orm.relation("Code", backref=(sql.orm.backref("signal", uselist=False)))
    daily_price = sql.orm.relation("DailyPrice", foreign_keys=[code_id, daily_price_date])
    prev_daily_price = sql.orm.relation("DailyPrice", foreign_keys=[code_id, prev_daily_price_date])

    @property
    def close_increment_by_1(self):
        return util.increment_by(self.close, 1)

    def close_increment_by_1m(self):
        return util.increment_by(self.close, -1)

    @property
    def buying_price_percent(self):
        if self.price:
            return util.increment(self.buying_price, self.price.close)

    @property
    def buying_price_2_percent(self):
        if self.price:
            return util.increment(self.buying_price_2, self.price.close)


class StockSplitDate(Base):

    __tablename__ = "stock_split_date"
    __table_args__ = (sql.PrimaryKeyConstraint("code_id", "date"), )

    from_number = sql.Column(sql.Integer, nullable=False)
    to_number = sql.Column(sql.Integer, nullable=False)
    date = sql.Column(sql.Date, nullable=False)
    code_id = sql.Column(
        sql.String(64),
        sql.ForeignKey(
            'code.id',
            ondelete='CASCADE',
            onupdate='NO ACTION'
        ),
        nullable=False
    )


# Orm Event
@sql.event.listens_for(Code, 'before_insert')
def code_before_insert(mapper, connection, code):
    s = sql.inspect(code).session
    splited = code.id.split("/", 2)
    if len(splited) == 2:
        db, _ = splited
        code.database = db

        @sql.event.listens_for(s, 'after_flush', once=True)
        def f(session, flush_context):
            code.signal = Signal()
