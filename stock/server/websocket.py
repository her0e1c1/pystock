import inspect
import tornado.websocket
from stock import query, util, charts, charts_params


def get_charts():
    return inspect.getmembers(charts, inspect.isfunction)


def to_json(m):
    return tornado.escape.json_decode(m)


class MainHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        self.write_message(util.json_dumps(dict(event="set_codes", codes=query.imported_quandl_codes())))

    def on_message(self, message):
        print(message)
        try:
            js = to_json(message)
        except ValueError:
            return
        if not isinstance(js, list):
            js = [js]
        for j in js:
            j["quandl_code"] = j.pop("code") if "code" in j else "NIKKEI/INDEX"
            query.store_prices_if_needed(j["quandl_code"])

            # OHLC
            s = query.get(price_type=None, **j)
            self.write_message(util.json_dumps(dict(j, **util.to_json(s))))

            for (c, f) in charts_params.get_charts().items():
                p = dict(price_type="close", chart_type=c, **j)
                ss = f(s["close"])
                self.write_message(util.json_dumps(dict(series=ss, **p)))

            # PREDICT
            s = query.predict(**j)
            self.write_message(util.json_dumps(dict(name="predict", series=s, **j)))

    def on_close(self):
        print("WebSocket closed")
