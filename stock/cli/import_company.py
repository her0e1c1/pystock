# coding: utf-8
import sqlalchemy as sql
import pandas as pd

from stock import models
from stock import util
from stock import config as C

from logging import getLogger
logger = getLogger(__name__)


class Reader(object):

    header = C.EXCEL_COMPANY_HEADER

    def __init__(self, filepath):
        excel = pd.ExcelFile(filepath)
        if C.SHEET_NAME not in excel.sheet_names:
            raise ValueError("The sheet %s doesn't exist in %s" % (C.SHEET_NAME, filepath))
        sheet = excel.parse(C.SHEET_NAME)

        if not self._check_header(sheet.columns):
            raise ValueError("invalid header")

        # convert japanese keys to model keys
        self.sheet = sheet.rename(columns=util.dict_inverse(self.header))
        self.filepath = filepath
        self.session = models.Session()

    def _check_header(self, row):
        return list(row) == list(self.header.values())

    def iter(self):
        for d in self.sheet.T.to_dict().values():
            yield {k: v for k, v in d.items() if k in models.Company.__dict__}

    def store(self):
        # TODO: exlucde duplicated code
        for data in self.iter():
            try:
                ins = models.Company(**data)
            except ValueError as e:
                logger.warn("The company whose code is %s is not imported: %s" % (data.get("code"), e))
            else:
                self.session.add(ins)
        try:
            self.session.commit()
        except sql.exc.IntegrityError as e:
            logger.warn("Can't import company data")
            logger.warn("%s" % e)
            return False
        return True


def update_copmany_list(start=None, end=None, each=False, ignore=False, last_date=None, limit=None):
    session = Session(ignore=ignore, each=each)
    for c in query.Company.all(last_date=last_date, session=session._s, limit=limit):
        _update_copmany(session, c)
    session.close()


def download_company_list(url=C.COMPANY_XLS_URL):
    from stock.cmd.import_company import Reader
    resp = requests.get(url)
    if resp.ok:
        return Reader(filepath=io.BytesIO(resp.content))


def download_and_store_company_list(url=C.COMPANY_XLS_URL):
    reader = download_company_list(url)
    if reader:
        return reader.store()
    else:
        return False
