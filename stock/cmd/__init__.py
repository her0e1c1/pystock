# coding: utf-8
import click

from stock import scrape
from stock import util
from stock import service
from stock import config as C


def _multiple_decorator(funcs):
    def wrap(g):
        for f in funcs:
            g = f(g)
    return wrap


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
        ctx.invoke(serve)


@cli.group()
def store():
    pass


@click.option("--url", default=C.COMPANY_XLS_URL)
@store.command(help="""\
You can download the xls at \
http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
or directly {url}
""".format(url=C.COMPANY_XLS_URL))
def company(url):
    if service.company.download_and_store_company_list(url):
        click.echo("Get %s" % url)
    else:
        click.echo("Can't get %s" % url)


@cli.group()
def db():
    pass


@db.command(help="Create new all tables")
def create():
    service.table.create()


@db.command(help="Drop all tables")
@click.option("-y", "yes", is_flag=True, default=False)
def drop(yes):
    if yes or click.confirm("Drop all tables. Are you sure?"):
        service.table.drop()


@cli.command(help="Setup")
@click.option("-l", "--limit", type=int, default=10)
@click.option("--all", is_flag=True, default=False)
def setup(all, limit):
    if all:
        limit = None
    click.echo("Start setup ...")
    click.echo("Create table ...")
    service.table.create()
    click.echo("Download and store company list ...")
    service.company.download_and_store_company_list()
    click.echo("Store day info")
    service.company.update_copmany_list(limit=limit, each=True, ignore=True)
    click.echo("Update search fields")
    service.search_field.update_search_fields()


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
@click.option("--host", default=C.HOST)
@click.option("-l", "--log-level", default=C.LOG_LEVEL, type=int)
@click.option("--debug", default=(not C.DEBUG), is_flag=True)
@cli.command(help="Start server")
def serve(**kw):
    from stock.server import app
    import logging
    msg = ", ".join(["%s = %s" % (k, v) for k, v in kw.items()])
    click.echo(msg)
    C.set(**kw)
    click.echo("DATABASE_URL: %s" % C.DATABASE_URL)
    logging.basicConfig(level=kw.pop("log_level"))
    app.run(**kw)


@cli.group(name="scrape")
def scrape_():
    pass

_decorator = _multiple_decorator([
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


@click.option("--limit", type=int, default=None)
@click.option("--each", is_flag=True, default=False)
@click.option("--no-field", is_flag=True, default=True)
@click.option("--last-date", callback=mkdate)
@cli.command(help="update day info")
def update(each, last_date, limit, no_field):
    if last_date is None:
        last_date = service.util.last_date()
    click.echo("update company list")
    service.company.update_copmany_list(each=True, ignore=True, last_date=last_date)
    if no_field:
        click.echo("update search fields")
        service.search_field.update_search_fields()


@cli.command(help="calculate everything", name="calc")
@click.option("--all", is_flag=True, default=False)
@click.option("--rcmc", "ratio_closing1_minus_closing2", is_flag=True, default=False)
@click.option("--bband", "closing_bollinger_band", is_flag=True, default=False)
@click.option("--rm25", "closing_minus_rolling_mean_25", is_flag=True, default=False)
@click.option("--rsi", "closing_rsi_14", is_flag=True, default=False)
@click.option("--min", "low_min", is_flag=True, default=False)
@click.option("-D", "closing_stochastic_d_minus_sd", is_flag=True, default=False)
@click.option("--macd", "closing_macd_minus_signal", is_flag=True, default=False)
@click.option("--lmc", "ratio_sigma_low_minus_closing", is_flag=True, default=False)
def calculate(**kw):
    # need to pop if it is not a service
    all = kw.pop("all")
    for method_name, do in kw.items():
        if all or do:
            meth = getattr(service.search_field, method_name, None)
            if meth:
                click.echo("CALC: %s" % method_name)
                meth()
            else:
                click.secho("CALC: %s is not found" % method_name, fg='red')


@cli.command(help="simulate", name="sm")
@click.argument('q', '--quandl-code', default="NIKKEI/INDEX")
@click.option("-p", '--price-type', default="close")
@click.option("--ratio", type=float)
@click.option("--lostcut", type=float)
@click.option("--start")
@click.option("--end")
def simulate(**kw):
    from stock.service.table import s
    s(**kw)


if __name__ == "__main__":
    cli()
