import pandas as pd
from stock.service import chart


def last(series, offset_from_last=0):
    i = series.last_valid_index()
    if i is None:
        return
    elif offset_from_last == 0:
        return series[i]
    elif i - offset_from_last >= 0:  # if index is datetime, then an error
        return series[i - offset_from_last]


def increment(a, b):
    if a is None or b is None:
        return
    # elif a.is_integer() and b.is_integer():  # I got float values here, too
    return float((a - b) / b) * 100


# Return "BUY", "SELL", NONE

def rolling_mean(series, period=25, ratio=25):
    """長期移動平均線と現在の株価の最終日の差がraito乖離したら売買シグナル"""
    mean = series.rolling(window=period, center=False).mean()
    r = increment(last(series), last(mean))
    return "BUY" if r > ratio else "SELL" if r < - ratio else None


def rsi(series, period=14, buy=30, sell=70):
    """RSIは基本的に30%以下で売られ過ぎ, 70%で買われ過ぎ"""
    rsi = chart.rsi(series, period)
    if rsi.empty:
        return None
    f = float(rsi[rsi.last_valid_index()])
    return "BUY" if f < buy else "SELL" if f > sell else None


def min(series, period=200, ratio=10):  # 200, 75, 25
    """指定期間中の最安値に近いたら買い. (底値が支えになって反発する可能性があると考える)"""
    m = float(series.tail(period).min())
    if pd.isnull(m):
        return None
    last = series[series.last_valid_index()]
    return "BUY" if increment(last, m) < ratio else None
