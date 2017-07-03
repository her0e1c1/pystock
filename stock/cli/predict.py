import os
import time
import click
from stock import query, util, params
from .main import cli, AliasedGroup


# @cli.group(cls=AliasedGroup, name="predict")
# def c():
#     pass


def get_url(code):
    u = os.environ.get("CHART_URL")
    return f"{u}?path=/chart&code={code}"


@cli.command(help="Predict prices")
@click.option("-s", "--signal-name", default="rolling_mean")
def predict(signal_name):
    funcs = params.get_signals()
    if signal_name not in funcs:
        click.echo("No signal: " + signal_name)
        return
    f = funcs[signal_name]
    for (code, prices) in query.get_prices_by_code():
        # util.send_to_slack(f"Predict {code}", "#logs")
        try:
            buy_or_sell = f(prices)
            if buy_or_sell in ["BUY", "SELL"]:
                url = get_url(code)
                util.send_to_slack(f"You should {buy_or_sell} {code} at {url} ({signal_name})")
        except Exception as e:
            util.send_to_slack(f"Error: Predict {code}({signal_name}): {e}")


@cli.command(help="Predict prices")
def hoge():
    print(query.get("TSE/1301"))
