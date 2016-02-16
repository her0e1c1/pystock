# coding: utf-8

import datetime

import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
import s.config as C


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
        return "{company_id}: {date} {closing}".format(**self.__dict__)

    @property
    def js_datetime(self):
        japan = self.date + datetime.timedelta(hours=9)
        return int(japan.strftime("%s")) * 1000

    def _fix_value(self, value):
        dates = self.company.split_stock_dates
        for date in dates:
            if self.date < date.date:
                value *= date.from_number / float(date.to_number)
        return value

    def fix_high(self):
        return self._fix_value(self.high)

    def fix_low(self):
        return self._fix_value(self.low)

    def fix_opening(self):
        return self._fix_value(self.opening)

    def fix_closing(self):
        return self._fix_value(self.closing)


class SplitStockDate(Base):
    """
    株分割した日
    """

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

    @sql.orm.validates('scale')
    def validate_scale(self, key, scale):
        if isinstance(scale, int):
            return scale
        elif isinstance(scale, float):
            return int(scale)
        else:
            raise ValueError("%s is not allowed for scale." % scale)

    def fix_data_frame(self):
        data_records = []
        for day_info in self.day_info_list:
            data = {
                "high": day_info.fix_high(),
                "low": day_info.fix_low(),
                "opening": day_info.fix_opening(),
                "closing": day_info.fix_closing(),
                "date":day_info.js_datetime}
            data_records.append(data)
        return pd.DataFrame.from_records(data_records)


class CurrentValue(Base):
    __tablename__ = "current_value"

    id = sql.Column(sql.Integer, primary_key=True)
    value = sql.Column(sql.Integer)
    datetime = sql.Column(sql.DateTime, nullable=False)
