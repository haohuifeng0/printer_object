# -*- coding: utf-8 -*-
from tornado.web import HTTPError


class AppError(HTTPError):

    def __init__(self, status, data=None, message=None,
                 log_message=None, *args, **kwargs):
        if message is None:
            message = MESSAGE[status] \
                if status in MESSAGE else "Unknown status."
        super(AppError, self).__init__(200, reason=message,
                                       log_message=log_message,
                                       *args, **kwargs)
        self.app_status_code = status
        self.data = data


# 请求被成功响应
OK = 200
# 请求格式错误，参数错误
ILLEGAL_FORMAT = 400
# 未认证
UNAUTHORIZED = 401
# 无权限访问该资源，请求失败
FORBIDDEN = 403
# 资源不存在
NOT_FOUND = 404
# 服务器错误
SERVER_ERROR = 500

MESSAGE = {
    OK: "Operation is successful.",
    ILLEGAL_FORMAT: "illegal format",
    UNAUTHORIZED: "Login required.",
    FORBIDDEN: "Permission is denied.",
    NOT_FOUND: "Not found.",
    SERVER_ERROR: "Server error.",
}
