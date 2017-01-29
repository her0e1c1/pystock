# coding: utf-8
import click
import pandas as pd

from .main import cli, mkdate
from stock import models, signals
from stock.service.simulate import RollingMean, MACD


def get(quandl_code, price_type):
    session = models.Session()
    query = session.query(models.Price).filter_by(quandl_code=quandl_code)
    df = pd.read_sql(query.statement, query.session.bind, index_col="date")
    series = getattr(df, price_type)
    return series


@cli.group()
def calc():
    pass


@calc.command(name="do")
@click.argument('quandl_code', default="NIKKEI/INDEX")
@click.option("-t", "--price-type", default="close")
@click.option("-s", "--start", callback=mkdate)
@click.option("-e", "--end", callback=mkdate)
@click.option("-m", "--method", default="macd")
def do(quandl_code, price_type, start, end, method):
    series = get(quandl_code, price_type)
    series = series.ix[start: end]
    ret = RollingMean(series).simulate()
    # parameterの調節で並列処理可能
    # ret = RollingMean(series, ratio=C.DEFAULT_ROLLING_MEAN_RATIO).simulate()
    print(ret)


# start/end dateを加える(index)
def s(quandl_code="NIKKEI/INDEX", price_type="close", way=None, lostcut=3, start=None, end=None, **kw):
    r = 0
    df = None
    # 一番儲けらるもの(パラメータの調節が必要なものもある.) and / or もできるようにしたい
    lists = [MACD(series)] + [RollingMean(series, i) for i in range(1, 10)]
    for l in lists:
        df_result = l.simulate_action()
        if df_result.empty:
            continue
        accumulation = df_result.ix[-1].accumulation
        if r < accumulation:
            r = max(r, accumulation)
            df = l
    return (r, df)


@calc.command(name="signal")
@click.argument('quandl_code', default="NIKKEI/INDEX")
@click.option("-t", "--price-type", default="close")
@click.option("-s", "--signal", default="rolling_mean")
def check_signal(quandl_code, price_type, signal):
    series = get(quandl_code, price_type)
    method = getattr(signals, signal)
    result = method(series=series)
    if result:
        click.secho(result)
        return result  # For now
