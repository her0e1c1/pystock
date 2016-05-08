import enum
from collections import OrderedDict
import pandas as pd


class Timing(enum.Enum):
    BUY = True
    SELL = False

# class Timing_(enum.Enum):
#     BUY = "buy"

#     SELL = "sell"
#     LOSTCUST = "lostcust"
#     FORCE = "force"


def increment_ratio(a2, a1):
    return ((a2 - a1) / a1) * 100


def timing(*series):
    return pd.concat(series, axis=1).T.apply(lambda x: x.all())


class Status(object):

    def __init__(self, simulator):
        self.simulator = simulator
        self.current = None
        self.accumulation = 0
        self.status = True

    def to_dict(self):
        return {
            "current": self.current,
            "accumulation": self.accumulation,
            "status": self.status
        }

    def is_lostcut(self, date):
        if self.current is None:
            return False
        price = self.simulator.series[date]
        return increment_ratio(price, self.current) <= -self.simulator.lostcut

    def finish(self):
        if self.current is None:
            return
        last = self.simulator.series.last_valid_index()
        self.sell(last)
        return False

    def buy(self, date):
        self.current = self.simulator.series[date]
        self.accumulation -= self.simulator.series[date]
        self.status = False

    def sell(self, date):
        self.current = None
        self.accumulation += self.simulator.series[date]
        self.status = True

    def is_buy(self, date):
        if date not in self.simulator.timing:
            return False
        return self.status and self.simulator.timing[date]

    def is_sell(self, date):
        if self.current is None:
            return False
        if date not in self.simulator.timing:
            return False
        return not self.status and not self.simulator.timing[date]


class Simulator(object):

    # ロストカットした場合は、トレンドの変化を確認してリセットする必要あり
    # 指標によっては、損切りした直後に買いシグナルが出る場合があるから
    def __init__(self,
                 series,
                 timing,
                 lostcut=3,
    ):
        self.series = series
        self.timing = timing
        self.lostcut = lostcut

    def simulate(self):
        result = []
        status = Status(simulator=self)
        for date in OrderedDict(self.series):
            tag = None
            if status.is_lostcut(date):
                status.sell(date)
                tag = "lostcut"
            elif status.is_buy(date):
                status.buy(date)
            elif status.is_sell(date):
                status.sell(date)
            else:
                continue
            result.append(dict(status.to_dict(), **{"date": date, "tag": tag}))
        if status.finish() is False:
            result.append(dict(status.to_dict(), **{"tag": "force"}))
        return pd.DataFrame(result)


class RollingMean(object):

    def __init__(self, series, ratio=10, period=25):
        self.series = series
        self.period = period
        self.ratio = ratio

    def run(self):
        mean = self.series.rolling(center=False, window=self.period).mean()
        return increment_ratio(mean, self.series)

    def buy(self):
        x = self.run()
        return x[x >= self.ratio]

    def sell(self):
        x = self.run()
        return x[-self.ratio >= x]

    def simulate(self):
        buy = self.buy().map(lambda x: True)
        sell = self.sell().map(lambda x: False)
        return Simulator(self.series, timing(buy, sell)).simulate()
