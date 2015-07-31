import time
import datetime

import click

from .import_company import Reader
from .store import set_info
from s import models


@click.group()
def cli():
    pass


@cli.group()
def store():
    pass


def mkdate(ctx, param, datestr):
    if datestr:
        t = time.strptime(datestr, "%Y-%m-%d")
        d = datetime.date.fromtimestamp(time.mktime(t))
        return d


@click.option("--start", callback=mkdate)
@click.option("--end", callback=mkdate)
@click.option("--code")
@store.command()
def stock(code, start, end):
    if code and start and end:
        set_info(code, start, end)


URL = "http://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/first-d-j.xls"
_help="""\
You can download the xls at http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
or directly {url}
""".format(url=URL)
@store.command(help=_help)
@click.argument('xls', type=click.Path(exists=True))
def company(xls):
    Reader(filepath=xls).store()


@cli.group()
def db():
    pass


@db.command(help="Create new all tables")
def create():
    models.Base.metadata.create_all()
