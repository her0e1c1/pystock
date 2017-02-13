import pandas as pd

from stock import charts


def test_rsi():
    def f(series, period=10):
        series = list(series)
        seq = charts.rsi(pd.Series(series), period=period)
        return seq[period]

    # 10日のデータには、差分を取るのに11日必要
    assert f(range(11)) == 100
    assert f(reversed(range(11))) == 0
    assert f([0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4]) == 70
    assert f([0, 1, 0, 1, 0, 1, 0, 1, 2, 3, 4]) == 70
