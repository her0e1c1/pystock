import pandas as pd
from . import line, util


def rolling_mean(series, period):
    """現在の株価(短期)と長期移動平均線(長期)のクロス"""
    slow = series.rolling(window=period, center=False).mean()
    return util.cross(series, slow)


def rolling_mean_ratio(series, period, ratio):
    """長期移動平均線と現在の株価の最終日の差がratio乖離したら売買シグナル"""
    mean = series.rolling(window=period, center=False).mean()
    r = util.increment(util.last(series), util.last(mean))
    return "BUY" if r > ratio else "SELL" if r < -ratio else None


def increment_ratio(series, ratio=25):
    """前日に比べてratio乖離してたら売買シグナル(変動が大きいので戻りの可能性が高いと考える)"""
    curr = util.last(series)
    prev = util.last(series, offset_from_last=1)
    r = util.increment(curr, prev)
    return "BUY" if r < -ratio else "SELL" if r > ratio else None


def rsi(series, period, buy, sell):
    """RSIは基本的に30%以下で売られ過ぎ, 70%で買われ過ぎ"""
    rsi = line.rsi(series, period)
    if rsi.empty:
        return None
    f = float(rsi[rsi.last_valid_index()])
    return "BUY" if f < buy else "SELL" if f > sell else None


def min_low(series, period, ratio):
    """指定期間中の最安値に近いたら買い. (底値が支えになって反発する可能性があると考える)"""
    m = float(series.tail(period).min())
    if pd.isnull(m):
        return None
    last = series[series.last_valid_index()]
    return "BUY" if util.increment(last, m) < ratio else None


def macd_signal(series, fast, slow, signal):
    """macd(短期)とsignal(長期)のクロス"""
    f = line.macd_line(series, fast, slow, signal)
    s = line.macd_signal(series, fast, slow, signal)
    return util.cross(f, s)


def stochastic(series, k, d, sd):
    """
    macd(短期)とsignal(長期)のクロス
    一般的に次の値を利用する (k, d, sd) = (14, 3, 3)
    """
    fast = line.stochastic_d(series, k=k, d=d)
    slow = line.stochastic_sd(series, k=k, d=d, sd=sd)
    return util.cross(fast, slow)


def bollinger_band(series, period=20, ratio=3):
    """
    2sigmaを超えたら、買われすぎと判断してSELL
    -2sigmaを超えたら、売られ過ぎと判断してBUY
    """
    s = util.sigma(series, period)
    return "BUY" if s <= -ratio else "SELL" if s >= ratio else None
