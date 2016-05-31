# coding: utf-8
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

from . import config as C
from . import wrapper


engine = sql.create_engine(C.DATABASE_URL, **C.CREATE_ENGINE)
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


class Price(Base):

    __tablename__ = "price"
    __table_args__ = (sql.UniqueConstraint('date', 'qcode'), )

    id = sql.Column(sql.Integer, primary_key=True)
    high = sql.Column(sql.Float, nullable=False)
    low = sql.Column(sql.Float, nullable=False)
    open = sql.Column(sql.Float, nullable=False)
    close = sql.Column(sql.Float, nullable=False)
    date = sql.Column(sql.Date, nullable=False)
    qcode = sql.Column(sql.String(64), nullable=False, index=True)
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

    id = sql.Column(sql.Integer, primary_key=True)

    ratio_closing1_minus_closing2 = sql.Column(sql.Float, nullable=True, index=True)
    ratio_closing_minus_rolling_mean_25 = sql.Column(sql.Float, nullable=True, index=True)
    closing_rsi_14 = sql.Column(sql.Float, nullable=True, index=True)
    ratio_1sigma_low_minus_closing = sql.Column(sql.Float, nullable=True, index=True)
    ratio_2sigma_low_minus_closing = sql.Column(sql.Float, nullable=True, index=True)

    # MACD
    closing_macd_minus_signal1_26_12_9 = sql.Column(sql.Float, nullable=True, index=True)
    closing_macd_minus_signal2_26_12_9 = sql.Column(sql.Float, nullable=True, index=True)

    # stochastic
    closing_stochastic_d_minus_sd1_14_3_3 = sql.Column(sql.Float, nullable=True, index=True)
    closing_stochastic_d_minus_sd2_14_3_3 = sql.Column(sql.Float, nullable=True, index=True)

    # (0, 1 sigma) => 1, (1 sigma, 2 sigma) => 2 and so on
    interval_closing_bollinger_band_20 = sql.Column(sql.Integer, nullable=True, index=True)

    low_min_25 = sql.Column(sql.Float, nullable=True, index=True)
    low_min_75 = sql.Column(sql.Float, nullable=True, index=True)
    low_min_200 = sql.Column(sql.Float, nullable=True, index=True)

    company_id = sql .Column(
        sql.Integer,
        sql.ForeignKey('company.id', onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    company = sql.orm.relation("Company", back_populates="search_field")

    @property
    def w(self):
        return wrapper.CompanySearchField(self)
