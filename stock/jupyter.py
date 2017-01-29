import matplotlib.pyplot as plt
from stock import query


def get(**kw):
    return query.get(**kw)


def show(**kw):
    series = get(**kw)
    plt.plot(series.index, series)


def drow():
    plt.figure(figsize=(15, 15))
