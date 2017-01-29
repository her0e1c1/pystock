# coding: utf-8
import click
from stock import query
from .main import cli, AliasedGroup


@cli.group(cls=AliasedGroup, name="query")
def c():
    pass


@c.command()
@click.argument('quandl_code')
def get(**kw):
    series = query.get(**kw)
    click.echo(series)


@c.command()
@click.option("-s", "--signal")
def signal(**kw):
    result = query.signal(**kw)
    click.echo(result)
