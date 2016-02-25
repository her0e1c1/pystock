# coding: utf-8
import click

from stock import models
from stock import query
from stock import scrape
from stock import util
from stock import service
from stock import config as C

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def mkdate(ctx, param, datestr):
    return util.str2date(datestr)


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


@click.option("--start", callback=mkdate)
@click.option("--end", callback=mkdate)
@click.option("--code")
@click.option("--each", is_flag=True, default=True)
@store.command()
def history(code, start, end, each):
    query.DayInfo.set(code, start, end, each=each)


@click.option("--url", default=C.COMPANY_XLS_URL)
@store.command(help="""\
You can download the xls at \
http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
or directly {url}
""".format(url=C.COMPANY_XLS_URL))
def company(url):
    if service.company.download_and_store_company_list(url):
        click.echo("Get %s" % C.COMPANY_XLS_URL)
    else:
        click.echo("Can't get %s" % C.COMPANY_XLS_URL)


@cli.group()
def db():
    pass


@db.command(help="Create new all tables")
def create():
    models.Base.metadata.create_all()


@db.command(help="Drop all tables")
@click.option("-y", "yes", is_flag=True, default=False)
def drop(yes):
    # this doesn't work
    # if click.confirm("Drop all tables. Are you sure?"):
    if yes:
        models.Base.metadata.drop_all()
    else:
        click.echo("Nothing")


@cli.command(help="Setup")
@click.option("--all", is_flag=True, default=False)
def setup(all):
    click.echo("Start setup ...")

    service.company.download_and_store_company_list()

    ctx = click.get_current_context()
    for cmd in [create, company]:
        ctx.invoke(cmd)


@cli.command(help="show companies")
@click.option("-c", "--closing-minus-rolling-mean-25", type=int)
def show(closing_minus_rolling_mean_25):
    iters = service.get_companies(
        closing_minus_rolling_mean_25=closing_minus_rolling_mean_25
    )
    for company in iters:
        click.echo(company)
    click.echo("Summary")
    click.echo("count: %s" % len(iters))


@click.option("--port", default=C.PORT, type=int)
@click.option("--debug", default=C.DEBUG, is_flag=True)
@cli.command(help="Start server")
def serve(port, debug):
    from stock.server import app
    app.run(port=port, debug=debug)


@cli.group(name="scrape")
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
    # 1日だけ更新する場合でも複数ページにアクセスする無駄を除くため、
    # last_dateを開始と終了日時に設定する
    query.DayInfo.sets(min_id=min_id, max_id=max_id,
                       each=each, ignore=True, last_date=last_date)


@cli.command(help="calculate everything", name="calc")
@click.option("--all", is_flag=True, default=False)
@click.option("--bband", "closing_bollinger_band", is_flag=True, default=False)
@click.option("--rm25", is_flag=True, default=False)
@click.option("--rsi", is_flag=True, default=False)
@click.option("--min", "low_min", is_flag=True, default=False)
@click.option("-D", "closing_stochastic_d_minus_sd", is_flag=True, default=False)
@click.option("--macd", "closing_macd_minus_signal", is_flag=True, default=False)
def calculate(**kw):
    for method_name, do in kw.items():
        if kw["all"] or do:
            logger.info("CALC: %s" % method_name)
            getattr(service.search_field, method_name)()
