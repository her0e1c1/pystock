
import tornado.websocket
from stock import query, util


def to_json(m):
    return tornado.escape.json_decode(m)


class MainHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        try:
            j = to_json(message)
        except ValueError:
            return
        series = query.get(**j)
        self.write_message(str(util.series_to_json(series)))

    def on_close(self):
        print("WebSocket closed")
