# coding: utf-8

# from stock import scrape
# from stock import util
# from stock import service
# from stock import config as C

from .main import cli
from . import database  # NOQA
from . import quandl  # NOQA
from . import server  # NOQA

# @cli.group()
# def store():
#     pass


# @click.option("--url", default=C.COMPANY_XLS_URL)
# @store.command(help="""\
# You can download the xls at \
# http://www.jpx.co.jp/markets/statistics-equities/misc/01.html
# or directly {url}
# """.format(url=C.COMPANY_XLS_URL))
# def company(url):
#     if service.company.download_and_store_company_list(url):
#         click.echo("Get %s" % url)
#     else:
#         click.echo("Can't get %s" % url)


# @cli.command(help="Setup")
# @click.option("-l", "--limit", type=int, default=10)
# @click.option("--all", is_flag=True, default=False)
# def setup(all, limit):
#     if all:
#         limit = None
#     click.echo("Start setup ...")
#     click.echo("Create table ...")
#     service.table.create()
#     click.echo("Download and store company list ...")
#     service.company.download_and_store_company_list()
#     click.echo("Store day info")
#     service.company.update_copmany_list(limit=limit, each=True, ignore=True)
#     click.echo("Update search fields")
#     service.search_field.update_search_fields()


# @cli.command(help="show companies")
# @click.option("-c", "--closing-minus-rolling-mean-25", type=int)
# def show(closing_minus_rolling_mean_25):
#     iters = service.get_companies(
#         closing_minus_rolling_mean_25=closing_minus_rolling_mean_25
#     )
#     for company in iters:
#         click.echo(company)
#     click.echo("Summary")
#     click.echo("count: %s" % len(iters))


# @click.option("--limit", type=int, default=None)
# @click.option("--each", is_flag=True, default=False)
# @click.option("--no-field", is_flag=True, default=True)
# @click.option("--last-date", callback=mkdate)
# @cli.command(help="update day info")
# def update(each, last_date, limit, no_field):
#     if last_date is None:
#         last_date = service.util.last_date()
#     click.echo("update company list")
#     service.company.update_copmany_list(each=True, ignore=True, last_date=last_date)
#     if no_field:
#         click.echo("update search fields")
#         service.search_field.update_search_fields()


# @cli.command(help="calculate everything", name="calc")
# @click.option("--all", is_flag=True, default=False)
# @click.option("--rcmc", "ratio_closing1_minus_closing2", is_flag=True, default=False)
# @click.option("--bband", "closing_bollinger_band", is_flag=True, default=False)
# @click.option("--rm25", "closing_minus_rolling_mean_25", is_flag=True, default=False)
# @click.option("--rsi", "closing_rsi_14", is_flag=True, default=False)
# @click.option("--min", "low_min", is_flag=True, default=False)
# @click.option("-D", "closing_stochastic_d_minus_sd", is_flag=True, default=False)
# @click.option("--macd", "closing_macd_minus_signal", is_flag=True, default=False)
# @click.option("--lmc", "ratio_sigma_low_minus_closing", is_flag=True, default=False)
# def calculate(**kw):
#     # need to pop if it is not a service
#     all = kw.pop("all")
#     for method_name, do in kw.items():
#         if all or do:
#             meth = getattr(service.search_field, method_name, None)
#             if meth:
#                 click.echo("CALC: %s" % method_name)
#                 meth()
#             else:
#                 click.secho("CALC: %s is not found" % method_name, fg='red')


# @cli.command(help="simulate", name="sm")
# @click.argument('q', '--quandl-code', default="NIKKEI/INDEX")
# @click.option("-p", '--price-type', default="close")
# @click.option("--ratio", type=float)
# @click.option("--lostcut", type=float)
# @click.option("--start")
# @click.option("--end")
# def simulate(**kw):
#     from stock.service.table import s
#     s(**kw)


if __name__ == "__main__":
    cli()
