# -*- coding: utf-8 -*-
import logging
import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

from apps.printer.handlers.datahandler import DataHandler
from libs.model import Base

TOP_DIR_ = os.path.abspath(os.path.join(__file__, "../../.."))

from apps.printer.handlers.main import *
from libs.confhelper import ConfHelper

define('port', type=int, default=6001)
define('conf', default=os.path.join(TOP_DIR_, "conf/global.conf"))
define('mode', default='deploy')


class Application(tornado.web.Application):
    def __init__(self, debug=False):
        handlers = [
            (r'/', MainHandler),
            (r'/data/*', DataHandler)
        ]

        settings = dict(
            debug=debug,
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        # self.db = connections["uweb"]


def shutdown(server):
    try:
        # old version of tornado does not support stop
        Base.metadata.drop_all()
        if hasattr(server, 'stop'):
            server.stop()
        tornado.ioloop.IOLoop.instance().stop
    except:
        pass


def main():
    tornado.options.parse_command_line()
    os.environ.setdefault("CONFIG_FILE", options.conf)
    if options.mode.lower() == "debug":
        debug_mode = True
    else:
        debug_mode = False

    http_server = None
    try:
        ConfHelper.load(options.conf)
        Base.metadata.create_all()
        application = Application(debug=debug_mode)
        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)

        http_server.listen(options.port)
        logging.warning("[PRINTER] running on: localhost:%d", options.port)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.error("Ctrl-C is pressed.")
    except:
        logging.exception("[PRINTER] exit exception")
    finally:
        logging.warning("[PRINTER] shutdown...")
        if http_server:
            shutdown(http_server)
        logging.warning("[PRINTER] Stopped. Bye!")


if __name__ == "__main__":
    main()

