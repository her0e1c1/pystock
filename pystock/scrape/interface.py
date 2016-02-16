from logging import getLogger

import requests
import bs4

from pystock.util import DateRange

logger = getLogger(__name__)


def clean_value(value):
    """文字列の数字を整数に変換する"""
    value = value.replace(",", "")
    return float(value)


class Scraper(object):

    def request(self, **kw):
        try:
            url = self.get_url(**kw)
            logger.info("GET: %s" % url)
            res = requests.get(url)
            soup = self._get_soup(res)
            values = self.parse(soup)
            return self.clean(values)
        except OSError:
            return None

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

    def split_stock_date(self, code, start=None, end=None):
        """
        :return:
            {"from_number": 株式分割前,
             "to_number": 株式分割後,
             "date": 分割日}
        """
        return self.SplitStockDate().request(code)

    def history(self, code, start=None, end=None, page=100):
        """:return: day_infoの戻り値と同じKEY-VALUEをもつ辞書のリスト"""
        d = DateRange(start, end)
        s = self.History()
        history = []
        for p in range(1, page + 1):
            day_info_list = list(s.request(code=code, p=p, **d.to_short_dict()))
            if day_info_list:
                history += day_info_list
            else:
                break
        return self.clean_history(history)

    def clean_current_value(self, current_value):
        return clean_value(current_value)

    def clean_day_info(self, day_info):
        if day_info:
            return {k: clean_value(v) if k != "date" else v for k, v in day_info.items()}

    def clean_history(self, history):
        return [self.clean_day_info(d) for d in history]
