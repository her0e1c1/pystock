import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from s import util


class Graph(object):

    @classmethod
    def month(cls, company, year, month):
        date = util.Date(year, month)
        dayinfos = company.range(date.first, date.last)
        manager = util.DayInfoManager(dayinfos)

        fig = plt.figure()
        loc = mdates.DayLocator()
        ax = fig.add_subplot(111)

        # labels = ax.get_xticklabels()
        # plt.setp(labels, rotation=30, fontsize=10)
        plt.xticks(rotation=30)

        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.grid(True)
        #ax.plot(list(zip(*manager.sequence_high)))
        xy = list(zip(*manager.sequence_high))
        fig.autofmt_xdate()
        ax.plot(*xy)

        filepath = util.graph_month_dir(company.code, year, month)
        plt.savefig(filepath)
