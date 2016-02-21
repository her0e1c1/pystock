import requests

from stock import config as C


def test_download_company_list():
    url = C.COMPANY_XLS_URL
    resp = requests.get(url)
    assert resp.ok
