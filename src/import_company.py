#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from collections import OrderedDict
import xlrd
import models


def main():
    p = argparse.ArgumentParser()
    p.add_argument("filepath", help="""\
$ ./import_company fiename.xls
:note: you can download xls at http://www.tse.or.jp/market/data/listed_companies/
""")
    args = p.parse_args()
    Reader(
        filepath=args.filepath
    ).store()


class Reader(object):

    header = OrderedDict([
        ("date", '日付'),
        ("code", 'コード'),
        ("name", '銘柄名'),
        ("category33", '33業種コード'),
        ("label33", '33業種区分'),
        ("category17", '17業種コード'),
        ("label17", '17業種区分'),
        ("scale", '規模コード'),
        ("label_scale", '規模区分'),
     ])
    ckeys = ["code", "name", "category17", "category33", "scale"]

    def __init__(self, filepath):
        self.filepath = filepath
        self.book = xlrd.open_workbook(filepath)
        self.company = models.Company
        self.session = models.initial_session()

    def _check_header(self, row):
        return [r.value for r in row] == list(self.header.values())

    def _map(self, row):
        d = dict(zip(self.header.keys(), row))
        return {k: v.value for k, v in d.items() if k in self.ckeys}

    def store(self, index=0):
        self._store(self.book.sheet_by_index(index))

    def _store(self, sheet):
        assert self._check_header(sheet.row(0)), "invalid header"

        for i in range(1, sheet.nrows):  # skip a header row
            row = sheet.row(i)
            ins = self.company(**self._map(row))
            self.session.add(ins)
        self.session.commit()

if __name__ == '__main__':
    main()
