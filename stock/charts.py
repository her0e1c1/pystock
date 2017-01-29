# coding: utf-8
import pandas as pd


def stochastic_k(prices, k=14):
    l = pd.rolling_min(prices, k)
    h = pd.rolling_max(prices, k)
    return 100 * (prices - l) / (h - l)


def stochastic_d(prices, k=14, d=3):
    return pd.rolling_mean(stochastic_k(prices, k), d)


def stochastic_sd(prices, k=14, d=3, sd=3):
    return pd.rolling_mean(stochastic_d(prices, k, d), sd)


def bollinger_band(prices, period, sigma=1):
    mean = pd.rolling_mean(prices, period)
    std = pd.rolling_std(prices, period)
    return mean + sigma * std


def macd_line(series, fast=26, slow=12, signal=9):
    # Chris Manning (fast, slow, signal) = (17, 9, 7)
    s = series.ewm(span=slow).mean()
    f = series.ewm(span=fast).mean()
    return s - f


def macd_signal(series, fast=26, slow=12, signal=9):
    """
    signalはmacdをさらに平準化したものなので、必ず長期
    """
    ml = macd_line(series, fast=fast, slow=slow, signal=signal)
    return ml.ewm(span=signal)


def rsi(series, period=14):
    """
    RSI＝(n日間の値上がり幅の合計) / (n日間の値上がり幅の合計＋n日間の値下がり幅の合計) * 100 %
    一般的にnは、14日を使用
    RSIが20～30%を下回ったら買い. 70-80%を上回ったら売り
    50&の時はそのperiodにおける売買の総和が両者等しい
    """
    def f(p):
        gain = p[p > 0].sum() / period
        loss = -p[p < 0].sum() / period
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    # fill 0 at the first day
    diff = (series - series.shift(1)).fillna(0)
    return diff.rolling(period).apply(func=f)
