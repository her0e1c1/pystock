import click
from bokeh.plotting import figure, output_file, show
from .main import cli, AliasedGroup
from stock import query


@cli.group(cls=AliasedGroup, name="show")
def c():
    pass


@c.command(name="code", help="Show code line")
@click.argument('quandl_code', default="NIKKEI/INDEX")
@click.option("-f", "--from-date")
@click.option("-t", "--to-date")
def show_by_code(quandl_code, **kw):
    output = "output.html"
    quandl_code = quandl_code.upper()  # FIXME
    series = query.get(quandl_code, **kw)
    if series.empty:
        click.secho("Not imported yet: %s" % quandl_code)
        return
    output_file(output)
    p = figure(x_axis_label="date", x_axis_type="datetime")
    p.line(series.index, series)
    show(p)
