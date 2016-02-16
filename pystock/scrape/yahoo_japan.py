import re

from .interface import Scraper, Interface

REG_SPLIT_STOCK_DATE = re.compile(r"分割\W+(?P<from_number>\d+)株.*?(?P<to_number>\d+)株")
REG_DATE = re.compile(r"(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日")


def parse_day_info(tr):
    td = [t.text for t in tr.findAll("td")]
    match = REG_DATE.match(td[0])
    if match:
        date = match.groupdict()
        return {
            "date": "{year}-{month}-{day}".format(**date),
            "opening": td[1],
            "high": td[2],
            "low": td[3],
            "closing": td[4],
            "volume": td[5],
        }


def parse_split_stock_date(tr):
    td = [t.text for t in tr.findAll("td")]
    match = REG_SPLIT_STOCK_DATE.match(td[1])
    date = parse_day_info(tr)
    if match and date:
        return {
            "from_number": match.group("from_number"),
            "to_number": match.group("to_number"),
            "date": "{year}-{month}-{day}".format(**date),
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
        for tr in span.next_sibling.findAll("tr")[1:]:  # skip header
            yield self._parse(tr)


class SplitStockDate(History):

    def _parse(self, tr):
        return parse_split_stock_date(tr)


class YahooJapan(Interface):
    scrapers = [SplitStockDate, History, CurrentValue]
