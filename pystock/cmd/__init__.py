import io
import logging

import click
import requests

from pystock import models
from pystock import query
from pystock import scrape
from pystock import util
from pystock import config as C

from .import_company import Reader


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        return util.str2date(datestr)


@click.option("--start", callback=mkdate)
@click.option("--end", callback=mkdate)
@click.option("--code")
@click.option("--each", is_flag=True, default=True)
@store.command()
def history(code, start, end, each):
    query.DayInfo.set(code, start, end, each=each)


@store.command(help="""\
You can download the xls at \
http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
or directly {url}
""".format(url=C.COMPANY_XLS_URL))
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


@cli.command(help="Setup")
@click.option("--all", is_flag=True, default=False)
def setup(all):
    click.echo("Start setup ...")
    ctx = click.get_current_context()
    for cmd in [create, company]:
        ctx.invoke(cmd)


@cli.command(help="show info")
@click.argument('code', type=int)
def show(code):
    for info in query.DayInfo.get(code):
        print(info.w)


@click.option("--port", default=C.PORT, type=int)
@click.option("--debug", default=C.DEBUG, is_flag=True)
@cli.command(help="Start server")
def serve(port, debug):
    from pystock.server import app
    app.run(port=port, debug=debug)


@cli.group()
def scrape_():
    pass

_decorator = util.multiple_decorator([
    click.option("--scraper", default=scrape.YahooJapan),
    click.option("--start"),
    click.option("--end"),
    click.argument('code', type=int)
])


@_decorator
@scrape_.command(name="history")
def scrape_history(code, start, end, scraper):
    history = scraper.history(code, start, end)
    for day_info in history:
        click.echo(day_info)


@_decorator
@scrape_.command(name="split")
def split_stock_date(code, start, end, scraper):
    history = scraper.split_stock_date(code, start, end)
    for day_info in history:
        click.echo(day_info)


@click.option("--scraper", default=scrape.YahooJapan)
@click.argument('code', type=int)
@scrape_.command(name="day_info")
def day_info(code, scraper):
    day_info = scraper.day_info(code)
    click.echo(day_info)


@click.option("--scraper", default=scrape.YahooJapan)
@click.argument('code', type=int)
@scrape_.command(name="value")
def current_value(code, scraper):
    value = scraper.current_value(code)
    click.echo(value)


@click.option("--max-id", type=int)
@click.option("--min-id", type=int, default=1)
@click.option("--each", is_flag=True, default=False)
@click.option("--last-date", callback=mkdate)
@cli.command(help="update day info")
def update(min_id, max_id, each, last_date):
    if max_id is None:
        max_id = query.Company.max_id()
    for id in range(min_id, max_id + 1):
        query.DayInfo.set(id, each=each, ignore=True)
