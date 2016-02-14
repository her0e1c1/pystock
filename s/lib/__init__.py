import io
import time
import datetime

import click
import requests
from dateutil import relativedelta

from .import_company import Reader
from .store import set_info, set_infos
from s import models
import s.config as C


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
    today = datetime.date.today()
    if start is None:
        start = today - relativedelta.relativedelta(years=1)
    if end is None:
        end = today

    if code:
        set_info(code, start, end)
    elif start and end:
        set_infos(start, end)


@store.command(help="""\
You can download the xls at \
http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
or directly {url}
""".format(url=C.COMPANY_XLS_URL)
)
def company():
    resp = requests.get(C.COMPANY_XLS_URL)
    if resp.ok:
        xls = resp.content
        Reader(filepath=io.BytesIO(xls)).store()
    else:
        click.echo("Can't get %s" % C.COMPANY_XLS_URL)


@cli.group()
def db():
    pass


@db.command(help="Create new all tables")
def create():
    models.Base.metadata.create_all()


@cli.command(help="Setup all")
def setup():
    click.echo("Start setup ...")
    ctx = click.get_current_context()
    for cmd in [create, company]:
        ctx.invoke(cmd)
