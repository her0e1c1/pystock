import requests

from stock import service
from stock import config as C


def test_download_company_list():
    url = C.COMPANY_XLS_URL
    resp = requests.get(url)
    assert resp.ok


def test_company_list_header():
    assert service.company.download_company_list()
