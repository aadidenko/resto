# -*- coding: utf-8 -*-
import tornado.httpclient


HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_ACCEPTED = 202
HTTP_STATUS_NO_CONTENT = 204
HTTP_STATUS_MULTIPLE_CHOICE = 300
HTTP_STATUS_SEE_OTHER = 303
HTTP_STATUS_NOT_MODIFIED = 304
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNATHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_METHOD_NOT_ALLOWED = 405
HTTP_STATUS_CONFLICT = 409
HTTP_STATUS_GONE = 410
HTTP_STATUS_UNPROCESSABLE_ENTITY = 422
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500
HTTP_STATUS_NOT_IMPLEMENTED = 501


class HttpResponse(tornado.httpclient.HTTPResponse):
    code = HTTP_STATUS_OK
    error_message = None

    def __init__(self, request, data=None, *args, **kwargs):
        url = getattr(request, 'url', request.uri)
        setattr(request, 'url', url)
        super(HttpResponse, self).__init__(request, self.code, *args, **kwargs)
        self._body = data


class HttpCreated(HttpResponse):
    code = HTTP_STATUS_CREATED

    def __init__(self, *args, **kwargs):
        location = kwargs.pop('location', None)
        super(HttpCreated, self).__init__(*args, **kwargs)
        if location is not None:
            self.headers['Location'] = location


class HttpOk(HttpResponse):
    code = HTTP_STATUS_OK


class HttpAccepted(HttpResponse):
    code = HTTP_STATUS_ACCEPTED


class HttpNoContent(HttpResponse):
    code = HTTP_STATUS_NO_CONTENT


class HttpMultipleChoice(HttpResponse):
    code = HTTP_STATUS_MULTIPLE_CHOICE


class HttpSeeOther(HttpResponse):
    code = HTTP_STATUS_SEE_OTHER


class HttpNotModified(HttpResponse):
    code = HTTP_STATUS_NOT_MODIFIED


class HttpBadRequest(HttpResponse):
    code = HTTP_STATUS_BAD_REQUEST


class HttpUnauthorized(HttpResponse):
    code = HTTP_STATUS_UNATHORIZED


class HttpForbidden(HttpResponse):
    code = HTTP_STATUS_FORBIDDEN


class HttpNotFound(HttpResponse):
    code = HTTP_STATUS_NOT_FOUND


class HttpMethodNotAllowed(HttpResponse):
    code = HTTP_STATUS_METHOD_NOT_ALLOWED


class HttpConflict(HttpResponse):
    code = HTTP_STATUS_CONFLICT


class HttpGone(HttpResponse):
    code = HTTP_STATUS_GONE


class HttpUnprocessableEntity(HttpResponse):
    code = HTTP_STATUS_UNPROCESSABLE_ENTITY


class HttpApplicationError(HttpResponse):
    code = HTTP_STATUS_INTERNAL_SERVER_ERROR


class HttpNotImplemented(HttpResponse):
    code = HTTP_STATUS_NOT_IMPLEMENTED
