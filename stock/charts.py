# coding: utf-8
import pandas as pd


def stochastic_k(series, k=14):
    rolling = series.rolling(window=k, center=False)
    l = rolling.min()
    h = rolling.max()
    return 100 * (series - l) / (h - l)


def stochastic_d(series, k=14, d=3):
    s = stochastic_k(series, k)
    return s.rolling(window=d, center=False).mean()


def stochastic_sd(series, k=14, d=3, sd=3):
    s = stochastic_d(series, k, d)
    return s.rolling(window=sd, center=False).mean()


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
    return ml.ewm(span=signal).mean()


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
