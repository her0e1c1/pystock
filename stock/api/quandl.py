import quandl
import requests
from .import error, util


def database():
    url = "https://www.quandl.com/api/v3/databases"
    r = requests.get(url)
    if not r.ok:
        msg = r.json()['quandl_error']['message']
        raise error.QuandlError(msg)
    codes = [j['database_code'] for j in r.json()['databases']]
    return codes


def quandl_codes(database_code):
    URL = "https://www.quandl.com/api/v3/databases/{}/codes.json".format(database_code)
    if quandl.ApiConfig.api_key:
        URL += "?api_key=" + quandl.ApiConfig.api_key
    r = requests.get(URL)
    if not r.ok:
        raise error.QuandlError(r.text)
    # row == [TSE/1111, "name"]
    codes = util.read_csv_zip(lambda row: row[0], content=r.content)
    return codes


MAP_PRICE_COLUMNS = {}
for v in ["open", "close", "high", "low"]:
    p = "price"
    keys = [v, v.title(), "%s %s" % (v, p), "%s %s" % (v.title(), p.title()), "%s%s" % (v.title(), p.title())]
    for k in keys:
        MAP_PRICE_COLUMNS[k] = v


def get_by_code(quandl_code):
    quandl_code = quandl_code.upper()
    data = quandl.get(quandl_code)
    data = data.rename(columns=MAP_PRICE_COLUMNS)
    data = data.reindex(data.index.rename("date"))  # "TSE/TOPIX" returns "Year" somehow
    data = data[pd.isnull(data.close) == False]  # NOQA
    data['quandl_code'] = quandl_code
    return data
