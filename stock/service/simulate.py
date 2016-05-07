import enum
import pandas as pd


class Timing(enum.Enum):
    BUY = True
    SELL = False

# class Timing_(enum.Enum):
#     BUY = "buy"
#     SELL = "sell"
#     LOSTCUST = "lostcust"


def increment_ratio(a, b):
    return ((a - b) / b) * 100


def timing(*series):
    return pd.concat(series, axis=1).T.apply(lambda x: x.all())


def simulate(series, timing):
    money = 0
    status = True
    for date, t in timing.to_dict().items():
        if status and t:
            money -= series[date]
            status = False
        elif not status and not t:
            money += series[date]
            status = True
    return money


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
        return increment_ratio(self.current, price) <= -self.simulator.lostcut

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
        for date, _ in self.series.to_dict().items():
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
        buy = self.buy()
        sell = self.sell()
        return Simulator(self.series, timing(buy, sell)).simulate()
