# coding: utf-8
from logging import getLogger

import requests
import bs4

from stock.util import DateRange

logger = getLogger(__name__)


class ParseError(Exception):
    pass


def clean_value(value):
    """文字列の数字を整数に変換する"""
    value = value.replace(",", "")
    return float(value)


class Scraper(object):

    def request(self, **kw):
        url = self.get_url(**kw)
        logger.info("GET: %s" % url)
        try:
            res = requests.get(url)
        except OSError:
            return None
        soup = self._get_soup(res)
        try:
            values = self.parse(soup)
        except ParseError as e:
            logger.warning("CAN NOT PARSE: %s" % e)
            return None
        return self.clean(values)

    def get_url(self, **kw):
        return self.url.format(**kw)

    def _get_soup(self, response):
        html = response.content.decode("utf-8").encode("utf-8")
        return bs4.BeautifulSoup(html, "html.parser")

    def parse(self, soup):
        raise NotImplementedError

    def clean(self, values):
        return values


class Meta(type):

    def __new__(cls, name, bases, attrs):
        for s in attrs.get("scrapers", []):
            attrs[s.__name__] = s
        return super(Meta, cls).__new__(cls, name, bases, attrs)


class Interface(object, metaclass=Meta):

    def current_value(self, code):
        """ :return: int """
        return self.clean_current_value(self.CurrentValue().request(code=code))

    def day_info(self, code):
        """
        :return:
            {"date": 株価の日付
             "opening": 始値,
             "high": 高値,
             "low": 安値,
             "closing": 終値,
             "volume": 出来高}
        """
        return self.clean_day_info(self.DayInfo().request(code=code))

    def _each_page(self, code, start, end, page, scraper):
        each = []
        for p in range(1, page + 1):
            r = scraper.request(
                code=code, p=p, **DateRange(start, end).to_short_dict())
            if r:
                each += r
            else:
                break
        return self.clean_history(each)

    def split_stock_date(self, code, start=None, end=None, page=100):
        """
        :return:
            {"from_number": 株式分割前,
             "to_number": 株式分割後,
             "date": 分割日}
        """
        return self._each_page(code, start, end, page, self.SplitStockDate())

    def history(self, code, start=None, end=None, page=100):
        """:return: day_infoの戻り値と同じKEY-VALUEをもつ辞書のリスト"""
        return self._each_page(code, start, end, page, self.History())

    def clean_current_value(self, current_value):
        return clean_value(current_value)

    def clean_day_info(self, day_info):
        if day_info:
            return {k: clean_value(v) if k != "date" else v for k, v in day_info.items()}

    def clean_history(self, history):
        return [self.clean_day_info(d) for d in history if d]
