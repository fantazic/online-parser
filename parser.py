import tornado.escape
import tornado.ioloop
import tornado.web
import os.path
import random
import string

from tornado.options import define, options, parse_command_line

define("port", default=8080, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        uploaded_file = self.request.files['file'][0]
        original_fname = uploaded_file['filename']
        extension = os.path.splitext(original_fname)[1]
        fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
        final_filename = fname+extension
        output_file = open("uploads/" + final_filename, 'w')
        output_file.write(uploaded_file['body'])
        self.finish("file" + final_filename + " is uploaded")


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/parser", MainHandler),
            (r"/parser/upload", UploadHandler),
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
