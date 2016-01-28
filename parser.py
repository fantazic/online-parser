import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import os.path
import logging

from tornado.options import define, options, parse_command_line

define("port", default=8080, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class FileHandler(tornado.websocket.WebSocketHandler):

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        logging.info("open a websocket")

    def on_close(self):
        logging.info("close a websocket")

    def on_message(self, message):
        logging.info("got message %r (%s)", message, type(message))

        if isinstance(message, str):
            rows = [line.split('\t') for line in (x.strip() for x in message.splitlines()) if line]
            self.write_message(tornado.escape.json_encode(rows))


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/parser/", MainHandler),
            (r"/parser/ws", FileHandler),
            ],
        cookie_secret="SX4gEWPE6bVr0vbwGtMl",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        debug=options.debug,
        )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
