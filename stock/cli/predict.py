import os
import time
import click
from stock import signals, query, util
from .main import cli, AliasedGroup


# @cli.group(cls=AliasedGroup, name="predict")
# def c():
#     pass


def get_url(code):
    u = os.environ.get("CHART_URL")
    return f"{u}?path=/chart&code={code}"


@cli.command(help="Predict prices")
def predict():
    for (code, prices) in query.get_prices_by_code():
        util.send_to_slack(f"Predict {code}", "#logs")
        buy_or_sell = signals.rolling_mean(prices)
        if buy_or_sell in ["BUY", "SELL"]:
            url = get_url(code)
            util.send_to_slack(f"You should {buy_or_sell} {code} at {url}")
