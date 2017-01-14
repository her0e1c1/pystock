# coding: utf-8
import click

from . import cli

from stock import models
from stock import service


@cli.group()
def db():
    pass


@db.command(help="Show env")
def env():
    from stock import models
    service.table.create()
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


# TODO: delete yesterday

@db.command(help="repl")
def repl():
    url = models.engine.url
    cmd = "mysql "
    cmd += "-h %s " % url.host
    cmd += "-u %s " % url.username
    if url.password:
        cmd += "-P'%s' " % url.password
    cmd += "%s " % url.database
    click.echo(cmd)
    # environ = os.environ.copy()
    # c = subprocess.Popen(cmd, env=environ, shell=True)
    # c.wait()
