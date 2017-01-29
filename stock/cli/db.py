# coding: utf-8
import click
from stock import models
from . import cli


session = models.Session()


@cli.group()
def db():
    pass


@db.command(help="Show env")
def env():
    models.create_all()
    tables = ", ".join(models.engine.table_names())
    summary = """\
url: {engine.url}
echo: {engine.echo}
name: {engine.name}
tables: {tables}
""".format(engine=models.engine, tables=tables)
    click.echo(summary)


@db.command(help="Create new all tables")
def create():
    models.create_all()


@db.command(help="Drop all tables")
@click.option("-y", "yes", is_flag=True, default=False)
def drop(yes):
    if yes or click.confirm("Drop all tables. Are you sure?"):
        models.drop_all()


@db.command(name="import")
def import_():
    import datetime
    today = datetime.date.today()
    for i in range(10):
        n = today + datetime.timedelta(days=i)
        session.add(models.Price(date=n, close=i, quandl_code="test"))
    session.commit()


@db.command(name="quandl_code", help="Store and show quandl code")
def quandl_code():
    codes = session.query(models.Price.quandl_code).distinct().all()
    click.secho(", ".join(c[0] for c in codes))
