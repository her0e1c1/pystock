# coding: utf-8
import click
from stock import query
from .main import cli, AliasedGroup


@cli.group(cls=AliasedGroup, name="predict")
def c():
    pass


@c.command(help="do")
@click.argument('quandl_code')
def do(**kw):
    result = query.predict(**kw)
    click.echo(result)
    return result
