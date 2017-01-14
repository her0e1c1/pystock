# coding: utf-8
import logging

import click

from stock import config as C
from .main import cli


@click.option("--port", default=C.PORT, type=int)
@click.option("--host", default=C.HOST)
@click.option("-l", "--log-level", default=C.LOG_LEVEL, type=int)
@click.option("--debug", default=(not C.DEBUG), is_flag=True)
@cli.command(help="Start server")
def serve(**kw):
    from stock.server import app
    msg = ", ".join(["%s = %s" % (k, v) for k, v in kw.items()])
    click.echo(msg)
    C.set(**kw)
    click.echo("DATABASE_URL: %s" % C.DATABASE_URL)
    logging.basicConfig(level=kw.pop("log_level"))
    app.run(**kw)
