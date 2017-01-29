# coding: utf-8
import click
from stock import models, query
from .main import cli, AliasedGroup


@cli.group(cls=AliasedGroup, name="predict")
def c():
    pass


@c.command(help="do")
def do():
    pass
