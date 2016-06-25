import enum


class PriceType(enum.Enum):
    open = "open"
    low = "low"
    high = "high"
    close = "close"


DEFAULT_ROLLING_MEAN_RATIO = 5


DATE_FORMATS = ["%Y/%m/%d", "%Y-%m-%d"]


MAP_PRICE_COLUMNS = {}
for v in ["open", "close", "high", "low"]:
    p = "price"
    keys = [v, v.title(), "%s %s" % (v, p), "%s %s" % (v.title(), p.title()), "%s%s" % (v.title(), p.title())]
    for k in keys:
        MAP_PRICE_COLUMNS[k] = v
