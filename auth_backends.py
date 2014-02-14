# -*- coding: utf-8 -*-

class DummyBackends(object):

    def is_authenticated(self, request, **kwargs):
        return True
