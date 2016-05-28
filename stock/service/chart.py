# coding: utf-8
import pandas as pd


def stochastic_k(prices, k):
    l = pd.rolling_min(prices, k)
    h = pd.rolling_max(prices, k)
    return 100 * (prices - l) / (h - l)


def stochastic_d(prices, k, d):
    return pd.rolling_mean(stochastic_k(prices, k), d)


def stochastic_sd(prices, k, d, sd):
    # (k, d, sd) = (14, 3, 3)
    return pd.rolling_mean(stochastic_d(prices, k, d), sd)


def bollinger_band(prices, period, sigma):
    mean = pd.rolling_mean(prices, period)
    std = pd.rolling_std(prices, period)
    return mean + sigma * std


def macd_line(series, fast=26, slow=12, signal=9):
    # Chris Manning (fast, slow, signal) = (17, 9, 7)
    return pd.ewma(series, span=slow) - pd.ewma(series, span=fast)


def macd_signal(series, fast=26, slow=12, signal=9):
    return pd.ewma(macd_line(series, fast=fast, slow=slow, signal=signal), span=signal)


def rsi(prices, period=14):
    # fill 0 at the first day
    diff = (prices - prices.shift(1)).fillna(0)

    def calc(p):
        gain =  p[p > 0].sum() / period
        loss = -p[p < 0].sum() / period
        rs = gain / loss
        return 100 - 100/(1+rs)

    return pd.rolling_apply(diff, period, calc)
