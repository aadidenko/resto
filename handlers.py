# -*- coding: utf-8 -*-
import sys
from tornado import escape
from tornado.escape import utf8
from tornado.web import RequestHandler
from resto import exceptions
from resto import http
from resto import auth
from resto import serializers
from resto import httputil


class BaseRESTHandler(RequestHandler):
    allowed_methods = []
    authentication = auth.Authentication()
    serializer = serializers.JSONSerializer()

    def _response(self, response):
        self._headers = response.headers
        self.set_status(response.code)
        meta = self._response_meta(error_message=response.error_message)
        data = response._body
        self.finish({
            'meta': meta,
            'response': data
        })

    def _response_meta(self, **kwargs):
        meta = {
            'status': self.get_status(),
        }

        if self.get_status() >= 400:
            error_message = kwargs.pop('error_message', None)
            meta['error'] = self._reason
            if error_message is not None:
                meta['message'] = error_message

        return meta

    def write(self, chunk):
        if self._finished:
            raise RuntimeError("Cannot write() after finish().  May be caused "
                               "by using async operations without the "
                               "@asynchronous decorator.")
        if isinstance(chunk, dict):
            chunk = self.serializer.serialize(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        chunk = utf8(chunk)
        self._write_buffer.append(chunk)

    def set_status(self, status_code, reason=None):
        """Sets the status code for our response.

        :arg int status_code: Response status code. If ``reason`` is ``None``,
            it must be present in `httplib.responses <http.client.responses>`.
        :arg string reason: Human-readable reason phrase describing the status
            code. If ``None``, it will be filled in from
            `httplib.responses <http.client.responses>`.
        """
        self._status_code = status_code
        if reason is not None:
            self._reason = escape.native_str(reason)
        else:
            try:
                self._reason = httputil.responses[status_code]
            except KeyError:
                raise ValueError("unknown status code %d", status_code)

    def head(self, *args, **kwargs):
        self.wrap_dispatch(request_method='head', **kwargs)

    def options(self, *args, **kwargs):
        self.wrap_dispatch(request_method='options', **kwargs)

    def get(self, *args, **kwargs):
        self.wrap_dispatch(request_method='get', **kwargs)

    def post(self, *args, **kwargs):
        self.wrap_dispatch(request_method='post', **kwargs)

    def put(self, *args, **kwargs):
        self.wrap_dispatch(request_method='put', **kwargs)

    def patch(self, *args, **kwargs):
        self.wrap_dispatch(request_method='patch', **kwargs)

    def delete(self, *args, **kwargs):
        self.wrap_dispatch(request_method='delete', **kwargs)

    def wrap_dispatch(self, **kwargs):
        try:
            response = self.dispatch(**kwargs)
        except exceptions.HttpApplicationError:
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
        except exceptions.RestoError as e:
            response = getattr(e, 'response', None)
            if response is not None:
                self._response(response)
        except Exception:
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
        else:
            self._response(response)

    def dispatch(self, request_method, **kwargs):
        method = self.method_check(request_method)

        dispatch_func = getattr(self, 'dispatch_%s' % method, None)

        if dispatch_func is None:
            raise exceptions.ImmediateHttpResponse(
                response=http.HttpNotImplemented(self.request)
            )

        self.is_authenticated()

        # TODO
        # self.throttle_check()

        response = dispatch_func(**kwargs)

        # TODO
        # self.log_throttle_access()

        if isinstance(response, http.HttpResponse):
            return response
        elif isinstance(response, dict):
            return self.create_http_response(response)
        else:
            return http.HttpNoContent(self.request)

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

        if not method in allowed_methods:
            response = http.HttpMethodNotAllowed(self.request)
            response.headers['Allow'] = allows
            raise exceptions.ImmediateHttpResponse(response=response)

        return method

    def is_authenticated(self):
        is_auth, user = self.authentication.is_authenticated(self.request)

        if not is_auth:
            raise exceptions.ImmediateHttpResponse(
                response=http.HttpUnauthorized(self.request)
            )
        else:
            self.user = user

    def serialize(self, data):
        return self.serializer.serialize(data)

    def dispatch_head(self, *args, **kwargs):
        return http.HttpMethodNotAllowed(self.request)

    def dispatch_options(self, *args, **kwargs):
        return http.HttpMethodNotAllowed(self.request)

    def dispatch_get(self, *args, **kwargs):
        return http.HttpMethodNotAllowed(self.request)

    def dispatch_post(self, *args, **kwargs):
        return http.HttpMethodNotAllowed(self.request)

    def dispatch_put(self, *args, **kwargs):
        return http.HttpMethodNotAllowed(self.request)

    def dispatch_patch(self, *args, **kwargs):
        return http.HttpMethodNotAllowed(self.request)

    def dispatch_delete(self, *args, **kwargs):
        return http.HttpMethodNotAllowed(self.request)


class RESTHandler(BaseRESTHandler):
    pass
