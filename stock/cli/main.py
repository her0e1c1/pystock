# coding: utf-8
import click
import quandl
from stock import util, models, params


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
    if key:
        quandl.ApiConfig.api_key = key


@cli.command()
def init():
    models.drop_all()
    models.create_all()


@cli.command()
def config(**kw):
    m = ", ".join(str(s) for (s, _) in params.get_signals().items())
    click.echo("SIGNALS: " + m)

    m = ", ".join(str(s) for (s, _) in params.get_lines().items())
    click.echo("LINES: " + m)
