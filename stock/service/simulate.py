import enum
from collections import OrderedDict
import pandas as pd
from stock.service import chart


DEFAULT_FIGSIZE = (10, 10)


class LineType(enum.Enum):

    rooling_mean = "rooling_mean"


class Action(enum.IntEnum):

    BUY = 1
    SELL = 2
    LOSTCUT = 3
    FORCE = 4
    NANPIN = 5

    @property
    def color(self):
        return dict(zip(Action, "rbgym")).get(self.value, "r")

    @classmethod
    def xlabel(cls):
        return 'color : %s' % ", ".join("{0.name} = {0.color}".format(a) for a in cls)

Timing = enum.IntEnum("Timing", "BUY SELL")


def increment_ratio(a2, a1):
    return ((a2 - a1) / a1) * 100


def timing(*series):
    return pd.concat(series, axis=1).T.apply(mapping)


def mapping(x):
    y = x[x.notnull()]
    y0 = y.ix[0]
    # if (y0 == y).all():  # error
    if (y == y0).all():
        return y0
    return None


class Status(object):

    def __init__(self, simulator):
        self.simulator = simulator
        self.current = None
        self.accumulation = 0
        self.action = None

    def to_dict(self):
        return {
            "current": self.current,
            "accumulation": self.accumulation,
            "action": self.action,
        }

    def is_lostcut(self, date):
        if self.current is None:
            return False
        price = self.simulator.series[date]
        return increment_ratio(price, self.current) <= -self.simulator.lostcut

    def finish(self):
        last = self.simulator.series.last_valid_index()
        self.sell(last)
        self.action = Action.FORCE

    def buy(self, date):
        self.current = self.simulator.series[date]
        self.accumulation -= self.simulator.series[date]
        self.action = Action.BUY

    def sell(self, date):
        # TODO: 売買手数料を考慮
        self.current = None
        self.accumulation += self.simulator.series[date]
        self.action = Action.SELL

    def lostcut(self, date):
        self.sell(date)
        self.action = Action.LOSTCUT

    def is_buy(self, date):
        if date not in self.simulator.timing:
            return False
        last = self.simulator.series.last_valid_index()
        if date == last:
            return False
        return (self.action in [None, Action.SELL, Action.LOSTCUT]) and self.simulator.timing[date] == Timing.BUY

    def is_sell(self, date):
        if self.current is None:
            return False
        if date not in self.simulator.timing:
            return False
        return self.action in [Timing.BUY] and self.simulator.timing[date] == Timing.SELL

    def is_finish(self):
        return self.current is not None


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

    def set_ax(self, ax):
        ax.set_title('Simulator')  # TODO: show qcode
        df = self.simulate()
        ymin, ymax = ax.get_ylim()
        for action in Action:
            signal = df.action[df.action == action]
            ax.vlines(x=signal.index, ymin=ymin, ymax=ymax - 1, color=action.color)
        ax.set_xlabel(Action.xlabel())
        return ax

    def simulate(self):
        s = self._simulate()
        return s
        return pd.concat([s, self.series], axis=1)

    def _simulate(self):
        result = []
        dates = []
        status = Status(simulator=self)
        for date in OrderedDict(self.series):
            if status.is_lostcut(date):
                status.lostcut(date)
            elif status.is_buy(date):
                status.buy(date)
            elif status.is_sell(date):
                status.sell(date)
            else:
                continue
            result.append(status.to_dict())
            dates.append(date)
        if status.is_finish():
            status.finish()
            result.append(status.to_dict())
            dates.append(date)
        return pd.DataFrame(result, index=dates)


class SignalLine(object):

    def __repr__(self):
        return self.__str__()

    def plot(self, figsize=DEFAULT_FIGSIZE, **kw):
        return self.df.plot(figsize=figsize)

    def set_ax(self, ax):
        ax.set_title('Rolling Mean')
        ymin, ymax = ax.get_ylim()
        ax.vlines(x=self.buy.index, ymin=ymin, ymax=ymax-1, color='r')
        ax.vlines(x=self.sell.index, ymin=ymin, ymax=ymax-1, color='b')
        return ax

    @property
    def timing(self):
        return timing(self.buy, self.sell)

    def simulate(self):
        return Simulator(self.series, self.timing).simulate()

    def simulate_action(self):
        df = Simulator(self.series, self.timing).simulate()
        if df.empty:
            return df
        notnull = df[df.action.notnull()]
        s = notnull['action'].map(lambda x: None if pd.isnull(x) else Action(x).name)
        return pd.concat([df.ix[s.index], s], axis=1)

    def simulate_plot(self):
        return Simulator(self.series, self.timing).set_ax(self.plot())


# ratio = [0, 100] => (1, 25)  # 最大幅以下しか取れない
# period = 25 or 30 days?  # 短期から長期にかけて計算できるようにする

class RollingMean(SignalLine):

    def __init__(self, series, ratio=10, period=25):
        self.series = series
        self.period = period
        self.ratio = ratio

    def __str__(self):
        return "RollingMean(period={period}, ratio={ratio})".format(**self.__dict__)

    __repr__ = __str__

    @property
    def df(self):
        return pd.concat({
            "series": self.series,
            "mean": self.mean
        }, axis=1)

    @property
    def mean(self):
        return self.series.rolling(center=False, window=self.period).mean()

    @property
    def iratio(self):
        return increment_ratio(self.mean, self.series)

    @property
    def buy(self):
        x = self.iratio
        return x[x >= self.ratio].map(lambda x: Timing.BUY)

    @property
    def sell(self):
        x = self.iratio
        return x[-self.ratio >= x].map(lambda x: Timing.SELL)


class MACD(SignalLine):

    def __init__(self, series, fast=26, slow=12, signal=9):
        self.series = series
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def __str__(self):
        return "MACD(fast={fast}, slow={slow}, signal={signal})".format(**self.__dict__)

    @property
    def df(self):
        # 単位が違うので、別々に表示する必要あり
        return pd.concat({
            "series": self.series,
            "macd": self.macd,
            "signal": self.signal_line,
        }, axis=1)

    @property
    def macd(self):
        return chart.macd_line(**self.__dict__)

    @property
    def signal_line(self):
        return chart.macd_signal(**self.__dict__)

    @property
    def cross(self):
        d = self.macd - self.signal_line
        return d[d * d.shift(1) < 0]

    @property
    def buy(self):
        c = self.cross
        return c[c > 0].map(lambda x: Timing.BUY)

    @property
    def sell(self):
        c = self.cross
        return c[c < 0].map(lambda x: Timing.SELL)
