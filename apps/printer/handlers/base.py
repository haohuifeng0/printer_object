# -*- coding: utf-8 -*-
import json

import tornado.web

from . import RESPONSE


class _DBDescriptor(object):
    def __get__(self, obj, type=None):
        return obj.application.db


class BaseHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

    # NOTE: use descriptor for db in order to override it in thread callbacks.
    db = _DBDescriptor()

    def write_data(self, data=None, meta=None, null=False):
        body = {'status': RESPONSE.OK,
                'message': RESPONSE.MESSAGE[RESPONSE.OK]}
        if data is not None:
            body['data'] = data
        elif null:
            body['data'] = None
        if meta is not None:
            body['meta'] = meta
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Expires", "0")
        self.write(json.dumps(body))

    def write_ret(self, status, message=None, dict_=None):
        """Write back ret message: dict(status=status,
                                   message=ErrorCode.ERROR_MESSAGE[status],
                                   ...)
        """
        ret = dict(status=status)

        if message is None:
            message = RESPONSE.MESSAGE[status]
        ret['message'] = message

        if dict_ and "message" in dict_:
            dict_.pop("message")
        if isinstance(dict_, dict):
            ret.update(dict_)

        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Expires", "0")
        self.write(json.dumps(ret))
