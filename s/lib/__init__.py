import os
import path
import time
import datetime

import click
import requests

from .import_company import Reader
from .store import set_info, set_infos
from s import models

ROOTDIR = path.Path(__file__).parent.parent.parent
COMPANY_XLS = ROOTDIR.joinpath(ROOTDIR, "company.xls")


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
    elif start and end:
        set_infos(start, end)


URL = "http://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
_help="""\
You can download the xls at http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
or directly {url}
""".format(url=URL)
@store.command(help=_help)
@click.argument('xls',
                default=COMPANY_XLS,
                type=click.Path(exists=True))
def company(xls):
    Reader(filepath=xls).store()


@store.command()
@click.argument('xls_path',
                default=COMPANY_XLS,
                type=click.Path(exists=False))
def download(xls_path):
    resp = requests.get(URL)
    if resp.ok:
        with open(xls_path, "wb") as f:
            f.write(resp.content)
        click.echo("get %s" % URL)
    else:
        click.echo("Can't get %s" % URL)


@cli.group()
def db():
    pass


@db.command(help="Create new all tables")
def create():
    models.Base.metadata.create_all()


def setup():
    pass
