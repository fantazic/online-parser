import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import os.path
import logging
import re
import csv

from tornado.options import define, options, parse_command_line

define("port", default=8080, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class FileHandler(tornado.websocket.WebSocketHandler):
    page_size = 100
    rows = []

    def make_message(self, page_no):
        return tornado.escape.json_encode({
            "page_no": page_no,
            "total_number": len(self.rows),
            "data": self.rows[self.page_size * (page_no - 1):self.page_size * page_no]
        })

    def check_origin(self, origin):
        return options.debug or bool(re.match(r'^.*\catlog\.kr', origin))

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        logging.info("open a websocket")

    def on_close(self):
        logging.info("close a websocket")

    def on_message(self, message):
        logging.info("got message")

        if isinstance(message, str):
            self.rows = [csv.reader([line], delimiter="\t").next()
                         for line in (x.strip() for x in message.splitlines()) if line]
            self.write_message(self.make_message(1))
        else:
            logging.info("page_no: " + message)
            page_no = int(message)
            self.write_message(self.make_message(page_no))


def main():
    parse_command_line()
    settings = dict(
            cookie_secret="SX4gEWPE6bVr0vbwGtMl",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=options.debug
    )

    handlers = [
            (r"/parser/", MainHandler),
            (r"/parser/ws", FileHandler),
            (r"/parser/static/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"]})
    ]

    app = tornado.web.Application(handlers, **settings)
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
