import tornado.websocket
from stock import query, util, params
from stock.models import QuandlCode, Price, Signal

LINES = params.get_lines()

s = util.schema
event_schema = s(QuandlCode, signal=s(
    Signal,
    price=Price,
    buying_price_percent=float,
    buying_price_2_percent=float,
))
price_schema = [s(Price)]


class MainHandler(tornado.websocket.WebSocketHandler):
    def __write(self, **kw):
        self.write_message(util.json_dumps(kw))

    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket open")

    def event_list(self, data):
        print(data)
        page = data.pop("page", 0)
        per_page = data.pop("per_page", 20)
        order_by = data.pop("order_by", None)  # TODO: validate
        asc = not data.pop("desc", False)
        detail = data.pop("detail", False)
        params = dict(
            from_date=data.pop("from", util.to_date(months=-1)),
            codes=data.pop("codes", []),
            page=page,
            per_page=per_page,
            order_by=order_by,
            asc=asc,
        )
        if not data.pop("chart", False):
            params.pop("from_date")
            qcodes = query.get_quandl_codes(**params)
            count = query.get_quandl_codes(count=True, **params)
            codes = util.schema_to_json([event_schema], qcodes)
        else:
            codes = []
            for qcode, groupby in query.get_prices_group_by_code(**params):
                prices = [p[1] for p in groupby]
                code = util.schema_to_json(event_schema, qcode)
                code["prices"] = util.schema_to_json(price_schema, prices)
                if detail:
                    lines = {"ohlc": code["prices"]}
                    df = util.models_to_dataframe(prices, index="date")
                    for (c, f) in LINES.items():
                        lines[c] = util.to_json(f(df.close))
                    code["chart"] = lines
                codes.append(code)
            # REFACTOR
            params.pop("from_date")
            qcodes = query.get_quandl_codes(**params)
            count = query.get_quandl_codes(count=True, **params)
        self.__write(**dict(data, codes=codes, count=count))
        print("DONE")

    def event_code(self, data):
        event = data.pop("event")
        line_names = data.pop("line", [])
        if not isinstance(line_names, list):
            line_names = [line_names]
        data["quandl_code"] = data.pop("code") if "code" in data else "NIKKEI/INDEX"
        query.store_prices_if_needed(data["quandl_code"])
        qcode = query.get_quandl_code(data["quandl_code"])
        if not qcode:
            return
        ohlc = query.get(price_type=None, **data)
        lines = {}
        for (c, f) in params.get_lines().items():
            if "all" in line_names or any([c.startswith(n) for n in line_names]):
                lines[c] = f(ohlc.close)
        self.__write(**dict(data, ohlc=ohlc, event=event, **lines))

    def on_message(self, message):
        try:
            js = tornado.escape.json_decode(message)
        except ValueError:
            return
        if not isinstance(js, list):
            js = [js]
        for j in js:
            if "event" in j:
                f = getattr(self, "event_" + j["event"], None)
                if f:
                    f(j)

    def on_close(self):
        print("WebSocket closed")
