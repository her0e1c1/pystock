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
            j = to_json(message)
        except ValueError:
            return
        t = j.pop("type", None)
        if t == "query":
            series = query.get(**j)
            self.write_message(util.json_dumps(series))
        else:
            print(f"No type: {t}")

    def on_close(self):
        print("WebSocket closed")
