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
            util.send_to_slack(f"Error: predict {code} ({signal_name}): {e}")
    for buy_or_sell, codes in result.items():
        if codes:
            query.set_signals(codes, **{signal_name: buy_or_sell})
            util.send_to_slack(f"You should {buy_or_sell} by {signal_name}: {codes}")
