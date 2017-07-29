import tornado.websocket
from stock import query, util, params
from stock.models import QuandlCode, Price, Signal

s = util.schema
event_list_schema = [s(QuandlCode, signal=s(Signal, price=Price))]


class MainHandler(tornado.websocket.WebSocketHandler):
    def __write(self, **kw):
        self.write_message(util.json_dumps(kw))

    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket open")

    def event_list(self, data):
        qcodes = query.get_quandl_codes()
        codes = util.schema_to_json(event_list_schema, qcodes)
        self.__write(**dict(data, codes=codes))

    def event_code(self, data):
        event = data.pop("event")
        data["quandl_code"] = data.pop("code") if "code" in data else "NIKKEI/INDEX"
        query.store_prices_if_needed(data["quandl_code"])
        qcode = query.get_quandl_code(data["quandl_code"])
        if not qcode:
            return
        ohlc = query.get(price_type=None, **data)
        lines = {}
        for (c, f) in params.get_lines().items():
            lines[c] = f(ohlc.close)
        self.__write(**dict(data, ohlc=ohlc, event=event, **lines))

        # # PREDICT
        # s = query.predict(**j)
        # self.write_message(util.json_dumps(dict(name="predict", series=s, **j)))

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
