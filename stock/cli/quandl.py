import time
import click
from .main import cli, AliasedGroup
from stock import query, api, error


@cli.group(cls=AliasedGroup, name="quandl")
def c():
    pass


@c.command(name="db", help="Store database codes")
def database():
    click.secho("Try to get database coe", fg="blue")
    try:
        codes = api.quandl.database()
    except error.QuandlError as e:
        click.secho(e, fg="red")
    else:
        click.echo(", ".join(sorted([c for c in codes])))


@c.command(name="code", help="Store and show quandl codes of [database_code] such as TSE, NIKKEI")
@click.argument('database_code')
def quandl_codes(database_code):
    qcodes = query.create_quandl_codes_if_needed(database_code)
    click.secho(", ".join(sorted([c.code for c in qcodes])))


@c.command(name="get", help="Store prices by calling quandl API")
@click.argument('quandl_code', default="NIKKEI/INDEX")
@click.option("-l", "--limit", type=int, default=None, help="For heroku db limitation")
@click.option("-f", "--force", type=bool, is_flag=True, default=False, help="Delete if exists")
def get_by_code(**kw):
    code = kw["quandl_code"]
    click.secho("TRY TO GET `%s`" % code)
    if query.store_prices_if_needed(**kw):
        click.secho("Imported: %s" % code)
    else:
        click.secho("Already imported: %s" % code)


@c.command(name="import_codes", help="import")
@click.argument('database_code')
@click.option("-s", "--sleep", type=int, default=60)
@click.option("-f", "--force", type=bool, is_flag=True, default=False, help="Delete if exists")
def import_codes(database_code, force, sleep):
    codes = query.get_quandl_codes()
    for c in codes:
        get_by_code.callback(c, force=force)
        time.sleep(sleep)
