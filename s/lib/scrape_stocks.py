# -*- coding: utf-8 -*-
import requests
import re
import bs4


def clean_value(value):
    """文字列の数字を整数に変換する"""
    value = value.replace(",", "")
    return float(value)


class Finance(object):
    # member
    url = None
    decode = "utf-8"
    country = "japan"

    def _request(self, api, **kw):
        url = self.get_url(**kw)
        try:
            res = requests.get(url)
            soup = self._get_soup(res)
            # HTMLのパース処理は子供のメソッドで行う
            parser = getattr(self, "parse_{}".format(api))
            cleaner = getattr(self, "clean_{}".format(api))
            values = parser(soup)
            return cleaner(values)
        except OSError:
            return None

    def _get_soup(self, response):
        html = response.content.decode(self.decode).encode("utf-8")
        soup = bs4.BeautifulSoup(html, "html.parser")
        return soup

    def get_url(self, **kw):
        return self.url.format(**kw)

    ## cleaner
    def clean_current_value(self, current_value):
        return clean_value(current_value)

    def clean_day_info(self, day_info):
        cleaned = {}
        for k, v in day_info.items():
            if k != "date":
                v = clean_value(v)
            cleaned[k] = v
        return cleaned

    def clean_history(self, history):
        cleaned = []
        for day_info in history:
            if day_info:
                cleaned.append(self.clean_day_info(day_info))
        return cleaned

    ## API
    def current_value(self, code):
         """
         :return: Int
         """
         return self._request("current_value", code=code)

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
        return self._request("day_info", code=code)

    def history(self, code, sy, sm, sd, ey, em, ed):
        """
        :return: day_infoの戻り値と同じKEY-VALUEをもつ辞書のリスト
        """
        history = []
        for p in range(1, 100):
            day_info_list = self._request("history", code=code, sy=sy, sm=sm, sd=sd, ey=ey, em=em, ed=ed, p=p)
            if day_info_list:
                history += day_info_list
            else:
                break
        #history.sort(key=lambda day_info: day_info["date"])
        return history


class YahooJapanFinance(Finance):
    url = "http://stocks.finance.yahoo.co.jp/stocks/detail/?code={code}.T"

    def parse_current_value(self, soup):
        value = soup.findAll("td", {"class": ["stoksPrice"]})[1].text
        return value


REG_SPLIT_STOCK_DATE = re.compile(ur"分割\W+(?P<from_number>\d+)株.*?(?P<to_number>\d+)株")
REG_DATE = re.compile(ur"(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日")
def _get_day_info(tr):

    td = [t.text for t in tr.findAll("td")]

    ## 分割の行の場合
    match_SPLIT_STOCK_DATE = REG_SPLIT_STOCK_DATE.match(td[1])
    ## 通所
    match_DATE = REG_DATE.match(td[0])

    if match_SPLIT_STOCK_DATE and match_DATE:
        date = match_DATE.groupdict()
        return  {
            "from_number": match_SPLIT_STOCK_DATE.group("from_number"),
            "to_number": match_SPLIT_STOCK_DATE.group("to_number"),
            "date": "{year}-{month}-{day}".format(**date),
        }

    if match_DATE:
        date = match_DATE.groupdict()
        return {
            "date": "{year}-{month}-{day}".format(**date),
            "opening": td[1],
            "high": td[2],
            "low": td[3],
            "closing": td[4],
            "volume": td[5],
        }


class HistoryYahooJapanFinance(Finance):
    url = "http://info.finance.yahoo.co.jp/history/?code={code}.T&sy={sy}&sm={sm}&sd={sd}&ey={ey}&em={em}&ed={ed}&tm=d&p={p}"

    def parse_history(self, soup):
        span = soup.find(True, {"class": "stocksHistoryPageing"})
        ls = []
        # headerはスキップ
        for tr in span.next_sibling.findAll("tr")[1:]:
            ls.append(_get_day_info(tr))
        return ls


class DayInfoYahooJapanFinance(Finance):
    url = "http://stocks.finance.yahoo.co.jp/stocks/history/?code={code}.T"

    def parse_day_info(self, soup):
        tr = soup.find("div", attrs={"id": "main"}).findAll("table")[1].findAll("tr")[1]
        return _get_day_info(tr)


class TokyoStockFinance(Finance):
    url = "http://quote.tse.or.jp/tse_n/quote.cgi?F=listing%2FJdetail1&QCODE={code}&MKTN=T"
    decode = "shift-jis"

    def parse_current_value(self, soup):
        a = soup.find("a", text=u"現在値 (時刻)")
        value_text = a.findParent("tr").findAll("td")[1].text
        value, time = value_text.replace(",", "").split()
        return value


if __name__ == "__main__":
    t = TokyoStockFinance()
    t = YahooJapanFinance()
    print(t.current_value(9984))
    # t1 = DayYahooJapanFinance()
    # print t1.day_info(9984)
    t2 = HistoryYahooJapanFinance()
    print(t2.history(9437, 2013, 1, 1, 2014, 1, 1))
