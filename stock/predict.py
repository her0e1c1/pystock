from . import util


# 値段予測(predict)
def predict(df, period=25, sigma=2):
    """
    ボリンジャーバンドの考え方を応用し、次の日の安値を予測する。
    前日の終値と現在の安値の差から、下落した場合の分散を算出。
    前日の終値は、この分散よりも下落しないだろうと判断し、買値目処とする。
    sigma=0を基準にすると、平均的な下値が算出される。ここが次の日の50%で購買できる買値
    """
    return predict_low(df.low, df.close.shift(1), period, sigma)


def predict_low(lows, highs, period=20, sigma=2):
    l = util.last(highs)
    if l is None:
        return
    d = lows - highs
    d = d[d < 0].tail(period)
    f = float(d.mean() - sigma * d.std())  # sigmaの幅
    return l + f
