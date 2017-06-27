import tornado.websocket
from stock import query, util, cli


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
            t = j.pop("type", None)
            if t == "query":
                series = query.get(**j)
                self.write_message(util.json_dumps(series))
            elif t == "get":
                query.store_prices(j.get("quandl_code", "NIKKEI/INDEX"))
                series = query.get(**j)
                self.write_message(util.json_dumps(series))
            else:
                print(f"No type: {t}")

    def on_close(self):
        print("WebSocket closed")
