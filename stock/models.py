# coding: utf-8
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

from . import config as C
from . import wrapper


engine = sql.create_engine(C.DATABASE_URL, **C.CREATE_ENGINE)
Base = declarative_base(bind=engine)
Session = sql.orm.sessionmaker(bind=engine)


def create_all():
    Base.metadata.create_all()


def drop_all():
    Base.metadata.drop_all()


class QuandlDatabase(Base):

    __tablename__ = "quandl_database"

    code = sql.Column(sql.String(64), primary_key=True)

    def __repr__(self):
        return "QuandlDatabase({code})".format(code=self.code)


class QuandlCode(Base):

    __tablename__ = "quandl_code"

    code = sql.Column(sql.String(64), primary_key=True)  # TSE/1234
    database_code = sql.Column(
        sql.String(64),
        sql.ForeignKey("quandl_database.code", onupdate="SET NULL", ondelete="SET NULL"),
        nullable=True,
    )
    database = sql.orm.relation('QuandlDatabase', backref="quandl_codes")

    def __repr__(self):
        return "QuandlCode({code})".format(**self.__dict__)

    @property
    def quandl_code(self):
        return "%s" % self.code


class StockExchange(Base):

    __tablename__ = "stock_exchange"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.Text, nullable=False)
    company = sql.orm.relationship(
        "Company",
        backref="stock_exchange",
        uselist=False
    )


class Price(Base):

    __tablename__ = "price"
    __table_args__ = (sql.UniqueConstraint('date', 'quandl_code'), )

    id = sql.Column(sql.Integer, primary_key=True)
    high = sql.Column(sql.Float, nullable=True)
    low = sql.Column(sql.Float, nullable=True)
    open = sql.Column(sql.Float, nullable=True)
    close = sql.Column(sql.Float, nullable=True)
    date = sql.Column(sql.Date, nullable=False)
    quandl_code = sql.Column(sql.String(64), nullable=False, index=True)
    volume = sql.Column(sql.Integer, nullable=True)


class DayInfo(Base):

    __tablename__ = "day_info"
    __table_args__ = (sql.UniqueConstraint('date', 'company_id'), )

    id = sql.Column(sql.Integer, primary_key=True)
    high = sql.Column(sql.Float, nullable=False)
    low = sql.Column(sql.Float, nullable=False)
    opening = sql.Column(sql.Float, nullable=False)
    closing = sql.Column(sql.Float, nullable=False)
    date = sql.Column(sql.Date, nullable=False)
    volume = sql.Column(sql.Integer, nullable=False)
    company_id = sql.Column(
        sql.Integer,
        sql.ForeignKey("company.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )
    company = sql.orm.relation(
        'Company',
        order_by='Company.id',
        uselist=False,
        backref='day_info_list'
    )

    def __str__(self):
        return "({company_id}, {opening}, {high}, {low}, {closing})".format(**self.to_dict())

    @property
    def w(self):
        return wrapper.DayInfo(self)


class SplitStockDate(Base):

    __tablename__ = "split_stock_date"
    __table_args__ = (sql.UniqueConstraint("date", "company_id"), )

    id = sql.Column(sql.Integer, primary_key=True)
    from_number = sql.Column(sql.Integer, nullable=False)
    to_number = sql.Column(sql.Integer, nullable=False)
    date = sql.Column(sql.Date, nullable=False)
    company_id = sql.Column(
        sql.Integer,
        sql.ForeignKey("company.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )
    company = sql.orm.relation(
        "Company",
        order_by="Company.id",
        uselist=False,
        backref="split_stock_dates"
    )


class Company(Base):

    __tablename__ = "company"
    __table_args__ = (sql.UniqueConstraint("code"), )

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.Text, nullable=False)
    description = sql.Column(sql.Text, nullable=True)
    code = sql.Column(sql.Integer)
    category17 = sql.Column(sql.Integer)
    category33 = sql.Column(sql.Integer)
    scale = sql.Column(sql.Integer, nullable=False)
    stock_exchange_id = sql.Column(
        sql.Integer,
        sql.ForeignKey('stock_exchange.id', onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    # search_field = sql.orm.relation(
    #     "CompanySearchField",
    #     uselist=False,
    #     back_populates="company"
    # )

    def __str__(self):
        return "({id}, {name}, {code})".format(**self.__dict__)

    @property
    def w(self):
        return wrapper.Company(self)

    @sql.orm.validates('scale')
    def validate_scale(self, key, scale):
        if isinstance(scale, int):
            return scale
        elif isinstance(scale, float):
            return int(scale)
        else:
            raise ValueError("%s is not allowed for scale." % scale)


class CurrentValue(Base):

    __tablename__ = "current_value"

    id = sql.Column(sql.Integer, primary_key=True)
    value = sql.Column(sql.Integer)
    datetime = sql.Column(sql.DateTime, nullable=False)
