# coding: utf-8
import click
import quandl
from stock import util
from stock import models
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
@click.option("-k", "--key", envvar='QUANDL_CODE_API_KEY')
def cli(key):
    ctx = click.get_current_context()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help(), color=ctx.color)
    if not models.engine.table_names():
        click.secho("No tables. So initiaize tables")
    if key:
        quandl.ApiConfig.api_key = key
    else:
        quandl.ApiConfig.api_key = C.QUANDL_CODE_API_KEY


@cli.command()
def init():
    models.drop_all()
    models.create_all()
