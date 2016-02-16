import io
import time
import datetime

import click
import requests

from .import_company import Reader
from .store import set_info, set_infos
from s import models
from s import query
import s.config as C


class AliasedGroup(click.Group):

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


@click.group(cls=AliasedGroup, invoke_without_command=True)
def cli():
    ctx = click.get_current_context()
    if ctx.invoked_subcommand is None:
        pass
        # ctx.invoke(default)


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


@cli.command(help="show info")
@click.argument('code', type=int)
def show(code):
    for info in query.DayInfo.get(code):
        print(info)


@cli.command(help="Start server")
def serve():
    from s.main import main
    main()


@cli.command(help="update day info")
def update():
    pass