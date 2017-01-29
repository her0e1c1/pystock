# coding: utf-8
import click
from stock import query, signals
from .main import cli, AliasedGroup


@cli.group(cls=AliasedGroup, name="config")
def c():
    pass


@c.command(name="signals")
def list_signals(**kw):
    m = ",".join(str(s) for s in signals.get_signals())
    click.echo(m)
