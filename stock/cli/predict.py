import os
import datetime
import click
from dateutil.relativedelta import relativedelta
from stock import query, util, params
from .main import cli, AliasedGroup


def get_url(code):
    u = os.environ.get("CHART_URL")
    return f"{u}?path=chart&code={code}"


@cli.command(help="Predict prices")
@click.option("-s", "--signal-name", default="rolling_mean")
def predict(signal_name):
    funcs = params.get_signals()
    if signal_name not in funcs:
        click.echo("No signal: " + signal_name)
        return
    result = {"BUY": [], "SELL": []}
    f = funcs[signal_name]
    kw = {"from_date": datetime.date.today() - relativedelta(months=3)}
    for code, df in query.get_all(**kw).groupby(level=0):
        try:
            buy_or_sell = f(df.close)
            if buy_or_sell in ["BUY", "SELL"]:
                result[buy_or_sell].append(code)
        except Exception as e:
            util.send_to_slack(f"ERROR: predict {code} ({signal_name}): {e}")
    for buy_or_sell, codes in result.items():
        if codes:
            query.bulk_update_signals(codes, **{signal_name: buy_or_sell})
            util.send_to_slack(f"You should {buy_or_sell} by {signal_name}: {codes}")


def last(s):
    last = s.tail(1)
    try:
        return float(last)
    except:
        return None


@cli.command(help="Predict prices")
def predict2():  # TODO: rename
    lines = params.get_lines()
    from stock import predict
    size = 100  # batch size
    kw = {"from_date": datetime.date.today() - relativedelta(months=3)}
    with query.models.session_scope() as s:
        for code in s.query(query.models.QuandlCode):
            codes = [code.code]
            print(codes)
            for code, group in query.get_prices_by_codes(s, codes=codes, **kw):
                if not (code and code.signal):
                    continue
                df = util.models_to_dataframe(list(group), index="date")
                p = predict.predict(df, sigma=0)
                p2 = predict.predict(df, sigma=1)
                code.signal.buying_price = p
                code.signal.buying_price_2 = p2
                code.signal.historical_volatility = last(lines["historical_volatility"](df.close))
                code.signal.std = last(lines["rolling_std"](df.close))
                code.signal.mean = last(lines["rolling_mean_25"](df.close))
                s.add(code.signal)


@cli.command(help="Do all commands at once")
def all():
    pass


@cli.command(name="sql")
@click.argument('name')
def _query(name):
    r = getattr(query, name)()
    print(list(r))
