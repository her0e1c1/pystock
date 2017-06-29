import time
import click
from stock import signals, query, util
from .main import cli, AliasedGroup


# @cli.group(cls=AliasedGroup, name="predict")
# def c():
#     pass


@cli.command(help="Predict prices")
@click.option("-s", "--sleep", type=int, default=60)
def predict(sleep):
    for (code, prices) in query.get_prices_by_code():
        buy_or_sell = signals.rolling_mean(prices)
        if buy_or_sell in ["BUY", "SELL"]:
            msg = f"You should {buy_or_sell} {code}"
            click.echo(msg)
            util.send_to_slack(msg)
        time.sleep(sleep)
