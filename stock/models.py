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


# Database code should be stored in key-value store
class QuandlCode(Base):

    __tablename__ = "quandl_code"

    code = sql.Column(sql.String(64), primary_key=True)  # TSE/1234

    # TODO: @property
    database_code = sql.Column(
        sql.String(64),
        nullable=True,
    )

    # TODO: rm
    @property
    def quandl_code(self):
        return self.code

    def __repr__(self):
        return "QuandlCode({code})".format(**self.__dict__)


class Price(Base):  # Daily Price

    __tablename__ = "price"
    __table_args__ = (sql.UniqueConstraint('date', 'quandl_code'), )

    high = sql.Column(sql.Float, nullable=True)
    low = sql.Column(sql.Float, nullable=True)
    open = sql.Column(sql.Float, nullable=True)
    close = sql.Column(sql.Float, nullable=True)
    date = sql.Column(sql.Date, nullable=False, index=True)
    quandl_code = sql.Column(sql.String(64), nullable=False, index=True)
    volume = sql.Column(sql.Integer, nullable=True)

    # FIXME:
    id = sql.Column(sql.Integer, primary_key=True)

    @sql.orm.validates('quandl_code')
    def validate_quandl_code(self, _key, val):
        return val.upper()


class CurrentPrice(Base):

    __tablename__ = "current_price"
    __table_args__ = (sql.UniqueConstraint('datetime', 'quandl_code'), )

    value = sql.Column(sql.Integer, nullable=False)
    datetime = sql.Column(sql.DateTime, nullable=False, index=True)
    quandl_code = sql.Column(sql.String(64), nullable=False, index=True)

    # FIXME:
    # sqlalchemy.exc.ArgumentError: Mapper Mapper|CurrentPrice|current_price could not assemble any primary key columns for mapped table 'current_price'
    id = sql.Column(sql.Integer, primary_key=True)


# class SplitStockDate(Base):

#     __tablename__ = "split_stock_date"
#     __table_args__ = (sql.UniqueConstraint("date", "company_id"), )

#     from_number = sql.Column(sql.Integer, nullable=False)
#     to_number = sql.Column(sql.Integer, nullable=False)
#     date = sql.Column(sql.Date, nullable=False)
#     quandl_code = sql.Column(sql.String(64), nullable=False, index=True)
