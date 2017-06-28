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
        print("WebSocket opened")

    def on_message(self, message):
        print(message)
        try:
            js = to_json(message)
        except ValueError:
            return
        if not isinstance(js, list):
            js = [js]
        for j in js:
            if "quandl_code" not in j:
                j["quandl_code"] = "NIKKEI/INDEX"

            query.store_prices_if_needed(j["quandl_code"])

            s = query.get(price_type="close", **j)
            self.write_message(util.json_dumps(dict(series=s, **j)))

            for (c, _f) in list(charts_params.get_charts().items())[:5]:
            # for (c, _f) in charts_params.get_charts().items():
                p = dict(price_type="close", chart_type=c, **j)
                s = query.get(**p)
                self.write_message(util.json_dumps(dict(series=s, **p)))

            # OHLC
            s = query.get(price_type=None, **j)
            self.write_message(util.json_dumps(dict(j, **util.to_json(s))))

            # PREDICT
            s = query.predict(**j)
            self.write_message(util.json_dumps(dict(name="predict", series=s, **j)))

    def on_close(self):
        print("WebSocket closed")
