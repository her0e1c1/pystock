import os

import pandas as pd
import click

import config as C
import models


@click.command()
@click.argument('excel')
def import_company(excel):
    """import company from an excel file which you can get."""
    click.echo(excel)
    reader = Reader(excel, C.EXCEL_COMPANY_HEADER)
    session = models.Session()
    for company_dict in reader.parse("Sheet1"):
        c = models.Company(**company_dict)
        session.add(c)
    session.commit()


class Reader(object):

    def __init__(self, filepath, header):
        assert os.path.isfile(filepath), "%s doesn't exist" % filepath
        self.filepath = filepath

        # convert japanese keys to model keys
        xls = pd.ExcelFile(filepath)
        self.xls = xls.rename(column=dict(header))

    def _check_header(self, row):
        return [r.value for r in row] == list(self.header.values())

    def parse(self, sheet_name):
        assert sheet_name in self.xls.sheet_names, "%s sheet doesn't exist" % sheet_name
        df = self.xls.parse(sheet_name)
        # assert self._check_header(sheet.row(0)), "invalid header"
        for company_dict in df.T.to_dict().values():
            yield company_dict
