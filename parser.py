import os.path
import logging
import re
import csv
import uuid

import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.locks
import tornado.gen

from tornado.options import define, options, parse_command_line

define("port", default=8080, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")

lock = tornado.locks.Lock()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class FileHandler(tornado.websocket.WebSocketHandler):
    clients = {}
    files = {}
    page_size = 100

    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        self.rows = []
        self.uuid = None

    @classmethod
    def send_message(cls, client_uuid, page_no):
        clients_with_uuid = cls.clients[client_uuid]
        logging.info("sending message to %d clients", len(clients_with_uuid))
        message = cls.make_message(client_uuid, page_no)

        for client in clients_with_uuid:
            try:
                client.write_message(message)
            except:
                logging.error("Error sending message", exc_info=True)

    @classmethod
    def load_file(cls, client_uuid, tsv_file):
        cls.files[client_uuid] = [csv.reader([line], delimiter="\t").next()
                                  for line in (x.strip() for x in tsv_file.splitlines()) if line]

    @classmethod
    def make_message(cls, client_uuid, page_no):
        rows = cls.files[client_uuid]
        return {
            "page_no": page_no,
            "total_number": len(rows),
            "data": rows[cls.page_size * (page_no - 1):cls.page_size * page_no]
        }

    @classmethod
    @tornado.gen.coroutine
    def add_clients(cls, client_uuid, client):
        # locking clients
        with (yield lock.acquire()):
            if client_uuid in cls.clients:
                clients_with_uuid = FileHandler.clients[client_uuid]
                FileHandler.clients[client_uuid] = clients_with_uuid.append(client)
            else:
                FileHandler.clients[client_uuid] = [client]

    @classmethod
    @tornado.gen.coroutine
    def remove_clients(cls, client_uuid, client):
        # locking clients
        with (yield lock.acquire()):
            if client_uuid in cls.clients:
                clients_with_uuid = FileHandler.clients[client_uuid]
                clients_removed = clients_with_uuid.remove(client)
                if len(clients_removed) == 0:
                    del cls.clients[client_uuid]
                else:
                    cls.clients[client_uuid] = clients_removed

            if client_uuid not in cls.clients and client_uuid in cls.files:
                del cls.files[client_uuid]

    def check_origin(self, origin):
        return options.debug or bool(re.match(r'^.*\catlog\.kr', origin))

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        logging.info("open a websocket")

        # Random UUID
        self.uuid = uuid.uuid4()
        FileHandler.add_clients(self.uuid, self)

    def on_close(self):
        logging.info("close a websocket")

        FileHandler.remove_clients(self.uuid, self)

    def on_message(self, message):
        logging.info("got message")

        if isinstance(message, str):
            FileHandler.load_file(self.uuid, message)
            page_no = 1
        else:
            logging.info("page_no: " + message)
            page_no = int(message)

        FileHandler.send_message(self.uuid, page_no)


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
