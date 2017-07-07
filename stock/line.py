
def rolling_mean(series, period):
    return series.rolling(window=period, center=False).mean()


def stochastic_k(series, k):
    rolling = series.rolling(window=k, center=False)
    l = rolling.min()
    h = rolling.max()
    return 100 * (series - l) / (h - l)


def stochastic_d(series, k, d):
    s = stochastic_k(series, k)
    return s.rolling(window=d, center=False).mean()


def stochastic_sd(series, k, d, sd):
    s = stochastic_d(series, k, d)
    return s.rolling(window=sd, center=False).mean()


def bollinger_band(prices, period, sigma):
    r = prices.rolling(window=period, center=False)
    return r.mean() + sigma * r.std()


def macd_line(series, fast, slow, signal):
    s = series.ewm(span=slow).mean()
    f = series.ewm(span=fast).mean()
    return s - f


def macd_signal(series, fast, slow, signal):
    """
    signalはmacdをさらに平準化したものなので、必ず長期
    """
    ml = macd_line(series, fast=fast, slow=slow, signal=signal)
    return ml.ewm(span=signal).mean()


def rsi(series, period):
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
