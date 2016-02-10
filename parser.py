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
    def get(self, client_uuid=""):
        logging.info("index with (uuid: %s)" % client_uuid)

        self.render("index.html", uuid=client_uuid)


class FileHandler(tornado.websocket.WebSocketHandler):
    clients = {}
    files = {}
    page_size = 100

    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        self.rows = []
        self.uuid = None

    @classmethod
    def send_messages(cls, client_uuid):
        clients_with_uuid = cls.clients[client_uuid]
        logging.info("sending message to %d clients", len(clients_with_uuid))

        message = cls.make_message(client_uuid)

        for client in clients_with_uuid:
            try:
                client.write_message(message)
            except:
                logging.error("Error sending message", exc_info=True)

    @classmethod
    def send_message(cls, client_uuid, client):
        clients_with_uuid = cls.clients[client_uuid]
        logging.info("sending message to %d clients", len(clients_with_uuid))

        message = cls.make_message(client_uuid)
        client.write_message(message)

    @classmethod
    def make_message(cls, client_uuid):
        rows = cls.files[client_uuid]["rows"]
        page_no = cls.files[client_uuid]["page_no"]

        return {
            "uuid": client_uuid,
            "page_no": page_no,
            "total_number": len(rows),
            "data": rows[cls.page_size * (page_no - 1):cls.page_size * page_no]
        }

    @classmethod
    def load_file(cls, client_uuid, tsv_file):
        rows = [csv.reader([line], delimiter="\t").next()
                                  for line in (x.strip() for x in tsv_file.splitlines()) if line]

        cls.files[client_uuid] = {"rows": rows, "page_no": 1}

    @classmethod
    @tornado.gen.coroutine
    def add_clients(cls, client_uuid, client):
        logging.info("add a client with (uuid: %s)" % client_uuid)

        # locking clients
        with (yield lock.acquire()):
            if client_uuid in cls.clients:
                clients_with_uuid = FileHandler.clients[client_uuid]
                clients_with_uuid.append(client)
            else:
                FileHandler.clients[client_uuid] = [client]

    @classmethod
    @tornado.gen.coroutine
    def remove_clients(cls, client_uuid, client):
        logging.info("remove a client with (uuid: %s)" % client_uuid)

        # locking clients
        with (yield lock.acquire()):
            if client_uuid in cls.clients:
                clients_with_uuid = FileHandler.clients[client_uuid]
                clients_with_uuid.remove(client)

                if len(clients_with_uuid) == 0:
                    del cls.clients[client_uuid]

            if client_uuid not in cls.clients and client_uuid in cls.files:
                del cls.files[client_uuid]

    def check_origin(self, origin):
        return options.debug or bool(re.match(r'^.*\catlog\.kr', origin))

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self, client_uuid=None):
        logging.info("open a websocket (uuid: %s)" % client_uuid)

        if client_uuid is None:
            # Generate a random UUID
            self.uuid = str(uuid.uuid4())

            logging.info("new client with (uuid: %s)" % self.uuid)
        else:
            self.uuid = client_uuid
            FileHandler.send_message(self.uuid, self)

            logging.info("new client sharing (uuid: %s)" % self.uuid)

        FileHandler.add_clients(self.uuid, self)

    def on_close(self):
        logging.info("close a websocket")

        FileHandler.remove_clients(self.uuid, self)

    def on_message(self, message):
        logging.info("got message (uuid: %s)" % self.uuid)

        if isinstance(message, str):
            FileHandler.load_file(self.uuid, message)
        else:
            logging.info("page_no: " + message)

            page_no = int(message)
            FileHandler.files[self.uuid]["page_no"] = page_no

        FileHandler.send_messages(self.uuid)


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
            (r"/parser/share/([^/]+)", MainHandler),
            (r"/parser/ws", FileHandler),
            (r"/parser/ws/([^/]+)", FileHandler),
            (r"/parser/static/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"]})
    ]

    app = tornado.web.Application(handlers, **settings)
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
