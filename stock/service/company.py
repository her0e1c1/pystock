# coding: utf-8
import io

import requests

from stock import query
from stock import config as C

from logging import getLogger
logger = getLogger(__name__)


def update_copmany_list():
    # check company_id is valid
    session = query.session()
    c = query.Company.all(last_date=last_date, session=session)
    if not c:
        logger.info("SKIP: company(id=%s)" % company_id)
        return
    session.close()


def download_and_store_company_list(url=C.COMPANY_XLS_URL):
    from stock.cmd.import_company import Reader
    resp = requests.get(url)
    if resp.ok:
        xls = resp.content
        return Reader(filepath=io.BytesIO(xls)).store()
    else:
        return False
