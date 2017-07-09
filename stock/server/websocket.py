import tornado.websocket
from stock import query, util, params


def to_json(m):
    return tornado.escape.json_decode(m)


class MainHandler(tornado.websocket.WebSocketHandler):
    def __write(self, **kw):
        self.write_message(util.json_dumps(dict(kw)))

    def check_origin(self, origin):
        return True

    def open(self):
        codes = query.imported_quandl_codes()
        self.__write(event="set_codes", codes=codes)

    def event_favorites(self, data):
        df = query.latest_prices_by_codes(data["codes"])
        d = {i: dict(df.ix[i]) for i in df.index}
        self.__write(**dict(data, event="favorites", **util.to_json(d)))

    def event_list(self, data):
        qcodes = query.get_quandl_codes()
        j = [dict(util.to_json(q), signal=q.signal) for q in qcodes]
        self.__write(**dict(data, codes=j))

    def on_message(self, message):
        print(message)
        try:
            js = to_json(message)
        except ValueError:
            return
        if not isinstance(js, list):
            js = [js]
        for j in js:
            if "event" in j:
                f = getattr(self, "event_" + j["event"], None)
                if f:
                    f(j)
                return

            j["quandl_code"] = j.pop("code") if "code" in j else "NIKKEI/INDEX"
            query.store_prices_if_needed(j["quandl_code"])
            qcode = query.get_quandl_code(j["quandl_code"])
            if not qcode:
                continue
            self.__write(event="signal", signal=qcode.signal)

            # OHLC
            s = query.get(price_type=None, **j)
            self.write_message(util.json_dumps(dict(j, **util.to_json(s))))

            for (c, f) in params.get_lines().items():
                p = dict(price_type="close", chart_type=c, **j)
                ss = f(s["close"])
                self.write_message(util.json_dumps(dict(series=ss, **p)))

            # PREDICT
            s = query.predict(**j)
            self.write_message(util.json_dumps(dict(name="predict", series=s, **j)))

    def on_close(self):
        print("WebSocket closed")
