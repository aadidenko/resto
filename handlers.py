# -*- coding: utf-8 -*-
import sys
import logging

from tornado import escape
from tornado.escape import utf8
from tornado.web import RequestHandler

from resto import exceptions
from resto import http
from resto import auth
from resto import serializers
from resto import httputil


logger = logging.getLogger('resto.handlers')


class BaseRESTHandler(RequestHandler):
    allowed_methods = []
    authentication = auth.Authentication()
    serializer = serializers.JSONSerializer()

    def __init__(self, *args, **kwargs):
        super(BaseRESTHandler, self).__init__(*args, **kwargs)
        self.current_user = None

    def _response(self, response):
        if self._finished:
            return

        self._headers = response.headers
        self.set_status(response.code)
        self.finish(response._body)

    def _execute(self, transforms, *args, **kwargs):
        """Executes this request with the given output transforms."""
        self._transforms = transforms
        try:

            self.path_args = [self.decode_argument(arg) for arg in args]
            self.path_kwargs = dict((k, self.decode_argument(v, name=k))
                                    for (k, v) in kwargs.items())

            self.dispatch(self.request.method, **kwargs)
        except Exception as e:
            self._handle_request_exception(e)

    def _handle_request_exception(self, e):
        self.log_exception(e, *sys.exc_info())

        if self._finished:
            return

        if isinstance(e, exceptions.RestoError):
            response = getattr(e, 'response', None)
            if response is not None:
                self._response(response)
        else:
            response = http.HttpApplicationError(self.request)

            if self.settings.get("debug"):
                import traceback

                self.set_status(http.HTTP_STATUS_INTERNAL_SERVER_ERROR)
                self.set_header('Content-Type', 'text/plain')
                for line in traceback.format_exception(*sys.exc_info()):
                    self.write(line)
                self.finish()
            else:
                self._response(response)

    def log_exception(self, e, typ, value, tb):
        # TODO
        # Logging exception
        logger.error(e)

    def write(self, chunk):
        if self._finished:
            raise RuntimeError("Cannot write() after finish().  May be caused "
                               "by using async operations without the "
                               "@asynchronous decorator.")

        if isinstance(chunk, dict) or isinstance(chunk, list):
            chunk = self.serializer.serialize(chunk)
            self.set_header("Content-Type", self.serializer.get_content_type())

        chunk = utf8(chunk)

        self._write_buffer.append(chunk)

    def set_status(self, status_code, reason=None):
        self._status_code = status_code
        if reason is not None:
            self._reason = escape.native_str(reason)
        else:
            try:
                self._reason = httputil.responses[status_code]
            except KeyError:
                raise ValueError("unknown status code %d", status_code)

    def head(self, *args, **kwargs):
        raise exceptions.HttpMethodNotAllowed(self.request)

    def options(self, *args, **kwargs):
        raise exceptions.HttpMethodNotAllowed(self.request)

    def get(self, *args, **kwargs):
        raise exceptions.HttpMethodNotAllowed(self.request)

    def post(self, *args, **kwargs):
        raise exceptions.HttpMethodNotAllowed(self.request)

    def put(self, *args, **kwargs):
        raise exceptions.HttpMethodNotAllowed(self.request)

    def patch(self, *args, **kwargs):
        raise exceptions.HttpMethodNotAllowed(self.request)

    def delete(self, *args, **kwargs):
        raise exceptions.HttpMethodNotAllowed(self.request)

    def dispatch(self, request_method, *args, **kwargs):
        method = self.method_check(request_method)

        func = getattr(self, method, None)
        if func is None:
            raise exceptions.ImmediateHttpResponse(
                response=http.HttpNotImplemented(self.request)
            )

        self.is_authenticated()

        self.throttle_check()

        response = func(**kwargs)

        self.log_throttle_access()

        if isinstance(response, http.HttpResponse):
            self._response(response)
        else:
            self._response(self.create_http_response(response))

    def create_http_response(self, data, response_class=http.HttpResponse):
        response = response_class(self.request)
        response._body = data
        return response

    def method_check(self, method):
        method = method.lower()

        allowed_methods = [meth.lower() for meth in self.allowed_methods]
        allows = ','.join(meth.upper() for meth in allowed_methods)

        if method == 'options':
            response = http.HttpResponse(self.request)
            response.headers['Allow'] = allows
            raise exceptions.ImmediateHttpResponse(response=response)

        if method not in self.SUPPORTED_METHODS and \
                not method in allowed_methods:
            response = http.HttpMethodNotAllowed(self.request)
            response.headers['Allow'] = allows
            raise exceptions.ImmediateHttpResponse(response=response)

        return method

    def is_authenticated(self):
        is_auth, user = self.authentication.is_authenticated(self.request)

        if not is_auth:
            self.current_user = None
            raise exceptions.ImmediateHttpResponse(
                response=http.HttpUnauthorized(self.request)
            )
        else:
            self.current_user = user

    def serialize(self, data):
        return self.serializer.serialize(data)

    def throttle_check(self):
        # TODO
        pass

    def log_throttle_access(self):
        # TODO
        pass


class RESTHandler(BaseRESTHandler):
    pass
