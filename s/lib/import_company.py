#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import click
from logging import getLogger

from s import models
import s.config as C

logger = getLogger(__name__)


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
        # TODO: exlucde duplicated code
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
