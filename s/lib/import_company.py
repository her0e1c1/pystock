#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import models
import click
import config as C
from logging import getLogger
logger = getLogger(__name__)


URL = "http://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/first-d-j.xls"

@click.command(
    help="""\
    You can download the xls at http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
    or directly {url}
    """.format(url=URL))
@click.argument('xls', type=click.Path(exists=True))
def import_company(xls):
    Reader(filepath=xls).store()


def inverse(dct):
    return {v: k for k, v in dct.items()}

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
        self.sheet = sheet.rename(columns=inverse(self.header))
        self.filepath = filepath
        self.session = models.Session()

    def _check_header(self, row):
        return all(row == list(self.header.values()))

    def iter(self):
        for d in self.sheet.T.to_dict().values():
            yield {k: v for k, v in d.items() if k in models.Company.__dict__}

    def store(self):
        for data in self.iter():
            try:
                ins = models.Company(**data)
            except ValueError as e:
                logger.warn("The company whose code is %s is not imported." % data.get("code"))
            else:
                self.session.add(ins)
        self.session.commit()

if __name__ == '__main__':
    import_company()
