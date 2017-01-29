# coding: utf-8
import click
from stock import util


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
def cli():
    ctx = click.get_current_context()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help(), color=ctx.color)
        ctx.exit()


# misc
# show_conf
@cli.command()
def jupyter():
    click.echo("""\
# Ret EDIT MODE
# C-Ret 実行
# S-Ret 実行(カーソル次)
# S-m 下のセルと統合
# x cut
# v paste
# j/k up/down

# EDIT MODE
# Ecs | C-m VIEW MODE

%matplotlib inline
import pandas as pd
import matplotlib.pyplot as plt
import imp
from stock import jupyter as j
""")
