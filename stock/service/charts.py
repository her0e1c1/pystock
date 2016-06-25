from stock import models

from stock import util
from stock import constant as C

from .simulate import RollingMean, MACD, timing
from .quandl import get_from_quandl


def get_series(quandl_code="NIKKEI/INDEX", price_type=C.PriceType.close, way=None, lostcut=3, start=None, end=None, **kw):
    if isinstance(start, str):
        start = util.str_to_date(start)
    if isinstance(end, str):
        end = util.str_to_date(end)
    if not isinstance(price_type, C.enum.Enum):
        price_type = C.PriceType(price_type)

    df = get_from_quandl(quandl_code, last_date=None)
    series = getattr(df, price_type.name)
    series = series.ix[start:end]
    return series
    # return RollingMean(series, ratio=kw.get("ratio", C.DEFAULT_ROLLING_MEAN_RATIO)).simulate()
