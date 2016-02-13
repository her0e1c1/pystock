import os
import datetime
from dateutil.relativedelta import relativedelta
import s.config as C


class Date(object):

    def __init__(self, year, month):
        self.first = datetime.date(year, month, 1)
        self.last = self.first + relativedelta(months=1, days=-1)

    def to_days(self):
        days = []
        if self.first < self.last:
            i = self.first
            while True:
                days.append(i)
                i += relativedelta(days=1)
                if i == self.last:
                    return days
        else:
            return []

    def __str__(self):
        return "from {first} to {last}".format(**self)


class DayInfoManager(object):

    def __init__(self, dayinfo_list):
        self.dayinfo_list = dayinfo_list

    def _sequence(self, key):
        for d in self.dayinfo_list:
            x = d.date
            y = getattr(d, key)
            yield (x, y)

    @property
    def sequence_high(self):
        return self._sequence("high")

    @property
    def sequence_low(self):
        return self._sequence("low")


def graph_month_dir(code, year, month, ext=".png"):
    name = C.FORMAT["month"].format(**locals())
    dir_ = C.FORMAT["image_dir"].format(code=code)
    if not os.path.isdir(dir_):
        os.makedirs(dir_)
    filepath = os.path.join(C.GRAPH_DIR, name + ext)
    return filepath
