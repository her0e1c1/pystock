# coding: utf-8
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

from . import config as C
from . import wrapper


engine = sql.create_engine(C.URL, **C.CREATE_ENGINE)
Base = declarative_base(bind=engine)
Session = sql.orm.sessionmaker(bind=engine)


class StockExchange(Base):
    __tablename__ = "stock_exchange"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.Text, nullable=False)
    company = sql.orm.relationship(
        "Company",
        backref="stock_exchange",
        uselist=False
    )


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
    search_field = sql.orm.relation(
        "CompanySearchField",
        uselist=False,
        back_populates="company"
    )

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


class CompanySearchField(Base):
    __tablename__ = "company_search_field"

    # WARN: postgresでは、大文字小文字を区別しないのでrsiをRSIなどと記述しない
    id = sql.Column(sql.Integer, primary_key=True)
    ratio_closing_minus_rolling_mean_25 = sql.Column(sql.Float, nullable=True)
    closing_rsi_14 = sql.Column(sql.Float, nullable=True)
    closing_macd_minus_signal1_26_12_9 = sql.Column(sql.Float, nullable=True)
    closing_macd_minus_signal2_26_12_9 = sql.Column(sql.Float, nullable=True)

    low_min_25 = sql.Column(sql.Float, nullable=True)
    low_min_75 = sql.Column(sql.Float, nullable=True)
    low_min_200 = sql.Column(sql.Float, nullable=True)

    company_id = sql .Column(
        sql.Integer,
        sql.ForeignKey('company.id', onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    company = sql.orm.relation("Company", back_populates="search_field")
