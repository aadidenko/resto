# -*- coding: utf-8 -*-
from resto.auth_backends import DummyBackends


class Authentication(object):
    backend = DummyBackends()

    def __init__(self, *args, **kwargs):
        backend = kwargs.pop('backend', None)
        if backend is not None:
            self.backend = backend

    def is_authenticated(self, request, **kwargs):
        user = self.backend.is_authenticated(request, **kwargs)
        return bool(user), user
