# coding: utf-8
import click
from .main import cli


@cli.group(name="scrape")
def scrape_():
    pass


_decorator = _multiple_decorator([
    click.option("--scraper", default=scrape.YahooJapan),
    click.option("--start"),
    click.option("--end"),
    click.argument('code', type=int)
])


@_decorator
@scrape_.command(name="history")
def scrape_history(code, start, end, scraper):
    history = scraper.history(code, start, end)
    for day_info in history:
        click.echo(day_info)


@_decorator
@scrape_.command(name="split")
def split_stock_date(code, start, end, scraper):
    history = scraper.split_stock_date(code, start, end)
    for day_info in history:
        click.echo(day_info)


@click.option("--scraper", default=scrape.YahooJapan)
@click.argument('code', type=int)
@scrape_.command(name="day_info")
def day_info(code, scraper):
    day_info = scraper.day_info(code)
    click.echo(day_info)


@click.option("--scraper", default=scrape.YahooJapan)
@click.argument('code', type=int)
@scrape_.command(name="value")
def current_value(code, scraper):
    value = scraper.current_value(code)
    click.echo(value)
