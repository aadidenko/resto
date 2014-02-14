# -*- coding: utf-8 -*-
from resto import http


class RestoError(Exception):
    pass


class ImmediateHttpResponse(RestoError):
    def __init__(self, response):
        self._response = response

    @property
    def response(self):
        return self._response


class RestoResponseError(RestoError):
    response_class = http.HttpResponse

    def __init__(self, request, **kwargs):
        self._response = self.response_class(request, **kwargs)

    @property
    def response(self):
        return self._response


class HttpBadRequest(RestoResponseError):
    response_class = http.HttpBadRequest


class HttpUnauthorized(RestoResponseError):
    response_class = http.HttpUnauthorized


class HttpForbidden(RestoResponseError):
    response_class = http.HttpForbidden


class HttpNotFound(RestoResponseError):
    response_class = http.HttpNotFound


class HttpUnprocessableEntity(RestoResponseError):
    response_class = http.HttpUnprocessableEntity


class HttpApplicationError(RestoResponseError):
    response_class = http.HttpApplicationError


class MissingParamError(HttpBadRequest):
    def __init__(self, request, param_name, *args, **kwargs):
        super(MissingParamError, self).__init__(request, *args, **kwargs)
        setattr(
            self._response,
            'error_message',
            "Missing `{}` param".format(param_name)
        )
