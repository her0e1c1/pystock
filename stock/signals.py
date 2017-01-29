import pandas as pd
from . import charts


# return pd.DataFrame.from_records([{}])


def get_signals():
    return ["rolling_mean", "rsi", "min_low", "macd_signal"]


# TODO: 呼び出し側でのNoneの考慮 + float()でwrapする?, invaid=Trueつける?
def last(series, offset_from_last=0):
    return _last(series, offset_from_last)


def _last(series, offset_from_last=0):
    if offset_from_last == 0:
        return series[-1]
    elif offset_from_last > 0:
        return series[-(offset_from_last + 1)]
    i = series.last_valid_index()  # .tail(1)使える?
    if i is None:  # or pd.isnull(i)
        return
    elif offset_from_last == 0:
        return series[i]
    elif i - offset_from_last >= 0:  # if index is datetime, then an error
        return series[i - offset_from_last]


def increment(a, b):
    if a is None or b is None:
        return None
    return float((a - b) / b) * 100


def sigma(series, period):
    """
    [-4, 4] or Noneを返す。
    つまり、
    現在値と平均が同じ => 0
    (0, 1] => 1
    (1, 2] => 2
    (2, 3] => 3
    (4,  ] => 4 (4sigma以上)
    また、負の方向はマイナスをつけるだけ
    """
    if series.empty:  # 他の関数にも書いたほうがいいかも(呼び出し側で気をつける?)
        return
    rolling = series.rolling(window=period, center=False)
    mean = last(rolling.mean())
    std = last(rolling.std())
    curr = last(series)
    if any([x is None for x in [curr, mean, std]]):
        return
    if curr == mean:
        return 0
    sign = 1 if curr > mean else -1
    for sigma in [1, 2, 3]:
        m1 = mean + sign * std * (sigma - 1)
        m2 = mean + sign * std * sigma
        if min(m1, m2) < curr <= max(m1, m2):  # fix import
            return sign * sigma
    else:
        return 4 * sign


# Return "BUY", "SELL", NONE
def cross(fast, slow):
    """
    golden cross: 短期が長期を下から上に抜けた場合(BUY)
    dead cross  : 短期が長期を上から下に抜けた場合(SELL)
    """
    f0 = last(fast)
    f1 = last(fast, offset_from_last=1)
    s0 = last(slow)
    s1 = last(slow, offset_from_last=1)
    if any([x is None for x in [f0, f1, s0, s1]]):
        return
    d0 = float(f0 - s0)
    d1 = float(f1 - s1)
    if d1 < 0 and d0 > 0:
        return "BUY"
    elif d1 > 0 and d0 < 0:
        return "SELL"


def rolling_mean(series, period=25):
    """現在の株価(短期)と長期移動平均線(長期)のクロス"""
    slow = series.rolling(window=period, center=False).mean()
    return cross(series, slow)


def rolling_mean_ratio(series, period=25, ratio=25):
    """長期移動平均線と現在の株価の最終日の差がratio乖離したら売買シグナル"""
    mean = series.rolling(window=period, center=False).mean()
    r = increment(last(series), last(mean))
    return "BUY" if r > ratio else "SELL" if r < -ratio else None


def increment_ratio(series, ratio=25):
    """前日に比べてratio乖離してたら売買シグナル(変動が大きいので戻りの可能性が高いと考える)"""
    curr = last(series)
    prev = last(series, offset_from_last=1)
    r = increment(curr, prev)
    return "BUY" if r < -ratio else "SELL" if r > ratio else None


def rsi(series, period=14, buy=30, sell=70):
    """RSIは基本的に30%以下で売られ過ぎ, 70%で買われ過ぎ"""
    rsi = charts.rsi(series, period)
    if rsi.empty:
        return None
    f = float(rsi[rsi.last_valid_index()])
    return "BUY" if f < buy else "SELL" if f > sell else None


def min_low(series, period=200, ratio=10):  # period in [200, 75, 25]
    """指定期間中の最安値に近いたら買い. (底値が支えになって反発する可能性があると考える)"""
    m = float(series.tail(period).min())
    if pd.isnull(m):
        return None
    last = series[series.last_valid_index()]
    return "BUY" if increment(last, m) < ratio else None


def macd_signal(series, **kw):
    """macd(短期)とsignal(長期)のクロス"""
    fast = charts.macd_line(series, **kw)
    slow = charts.macd_signal(series, **kw)
    return cross(fast, slow)


def stochastic(series, k=14, d=3, sd=3):
    """
    macd(短期)とsignal(長期)のクロス
    一般的に次の値を利用する (k, d, sd) = (14, 3, 3)
    """
    fast = charts.stochastic_d(series, k=k, d=d)
    slow = charts.stochastic_sd(series, k=k, d=d, sd=sd)
    return cross(fast, slow)


def bollinger_band(series, period=20, ratio=3):
    """
    2sigmaを超えたら、買われすぎと判断してSELL
    -2sigmaを超えたら、売られ過ぎと判断してBUY
    """
    s = sigma(series, period)
    return "BUY" if s <= -ratio else "SELL" if s >= ratio else None


def predict(df, period=20, sigma=2):
    """
    ボリンジャーバンドの考え方を応用し、次の日の安値を予測する。
    前日の終値と現在の安値の差から、下落した場合の分散を算出。
    前日の終値は、この分散よりも下落しないだろうと判断し、買値目処とする。
    """
    return predict_low(df.low, df.close.shift(1), period, sigma)


def predict_low(lows, highs, period=20, sigma=2):
    l = last(highs)
    if l is None:
        return
    d = lows - highs
    d = d[d < 0][:period]
    f = float(d.mean() - sigma * d.std())  # fはsigmaの幅
    return l + f
