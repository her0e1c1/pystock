# coding: utf-8
import re

from .interface import Scraper, Interface, ParseError

REG_SPLIT_STOCK_DATE = re.compile(r"分割\W+(?P<from_number>\d+)株.*?(?P<to_number>\d+)株")
REG_DATE = re.compile(r"(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日")


def _match_date(td):
    match = REG_DATE.match(td)
    if not match:
        raise ParseError("Not match date. %s" % td)
    return "{year}-{month}-{day}".format(**match.groupdict())


def parse_day_info(tr):
    tds = [t.text for t in tr.findAll("td")]
    if len(tds) == 2:
        return  # skip split stock date
    elif len(tds) != 7:
        raise ParseError("Can't parse day info. Need 7 columns. %s" % tr)
    return {
        "date": _match_date(tds[0]),
        "opening": tds[1],
        "high": tds[2],
        "low": tds[3],
        "closing": tds[4],
        "volume": tds[5],
    }


def parse_split_stock_date(tr):
    tds = [t.text for t in tr.findAll("td")]
    if len(tds) == 7:
        return  # skip day info
    elif len(tds) != 2:
        raise ParseError("Can't parse day info. Need 2 columns. %s" % tr)
    match = REG_SPLIT_STOCK_DATE.match(tds[1])
    if not match:
        raise ParseError("Not match split stock date. %s" % tds[1])
    return {
        "date": _match_date(tds[0]),
        "from_number": match.group("from_number"),
        "to_number": match.group("to_number"),
    }


class CurrentValue(Scraper):
    url = "http://stocks.finance.yahoo.co.jp/stocks/detail/?code={code}.T"

    def parse(self, soup):
        return soup.findAll("td", {"class": ["stoksPrice"]})[1].text


class History(Scraper):
    url = ("http://info.finance.yahoo.co.jp/history/?code={code}.T&"
           "sy={sy}&sm={sm}&sd={sd}&ey={ey}&em={em}&ed={ed}&tm=d&p={p}")

    def _parse(self, tr):
        return parse_day_info(tr)

    def parse(self, soup):
        span = soup.find(True, {"class": "stocksHistoryPageing"})
        if span is None:
            raise ParseError("Can't find css class stocksHistoryPageing")
        return [self._parse(tr) for tr
                in span.next_sibling.findAll("tr")[1:]]  # skip header


class SplitStockDate(History):

    def _parse(self, tr):
        return parse_split_stock_date(tr)


class YahooJapan(Interface):
    scrapers = [SplitStockDate, History, CurrentValue]
