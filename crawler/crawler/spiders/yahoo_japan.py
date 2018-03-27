import re
import urllib
import datetime
import scrapy
import scrapy_splash
from dateutil import relativedelta
import stock

URL = ("http://info.finance.yahoo.co.jp/history/?code={code}.T&"
       "sy={sy}&sm={sm}&sd={sd}&ey={ey}&em={em}&ed={ed}&tm=d")

REG_SPLIT_STOCK_DATE = re.compile(r"分割\W+(?P<from_number>\d+)株.*?(?P<to_number>\d+)株")
REG_DATE = re.compile(r"(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日")


def parse_date(text):
    match = REG_DATE.match(text)
    if match:
        converted = {k: int(v) for k, v in match.groupdict().items()}
        return datetime.date(**converted)


class YahooJapanSpider(scrapy.Spider):
    """
    Command line:
    $ scrapy crawl yahoo_japan -a code=CODE -a start=YYYY/MM/DD -a end=YYYY/MM/DD
    """

    name = "yahoo_japan"
    allowed_domains = ['info.finance.yahoo.co.jp']

    def __init__(self, **kwargs):
        end = kwargs.pop("end", None)
        end = stock.util.str2date(end, datetime.date.today())
        start = kwargs.pop("start", None)
        start = stock.util.str2date(start, end - relativedelta.relativedelta(month=1))
        code = kwargs.pop("code", None)
        self.params = {
            "end": end,
            "start": start,
            "codes": [code] if code else []
        }
        super().__init__(**kwargs)

    def start_requests(self):
        for code in self.params["codes"]:
            end = self.params["end"]
            sta = self.params["start"]
            url = URL.format(
                code=code,
                ey=end.year,
                em=end.month,
                ed=end.day,
                sy=sta.year,
                sm=sta.month,
                sd=sta.day,
            )
            yield scrapy_splash.SplashRequest(url=url, callback=self.parse)
            # yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        header = ["date", "open", "high", "low", "close", "volume", "adjust"]
        x1 = "//tr[th[contains(text(), '日付')] and th[contains(text(), '安値')]]/following-sibling::tr"
        x2 = "./td/text()"
        x3 = "//a[text() = '次へ']/@href"
        for tr in response.xpath(x1):
            data = [t.get() for t in tr.xpath(x2)]
            result = dict(zip(header, data))
            result.pop("adjust")
            result = {k: v.replace(",", "") for k, v in result.items()}
            result["date"] = parse_date(result["date"])
            query = urllib.parse.urlparse(response.url).query
            code = urllib.parse.parse_qs(query).get("code", [""])[0][:-2]
            result["quandl_code"] = "TSE/%s" % code
            yield result

        href = response.xpath(x3)
        if href:
            yield response.follow(href.get(), self.parse)
