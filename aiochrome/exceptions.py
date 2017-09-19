#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class AioChromeException(Exception):
    pass


class UserAbortException(AioChromeException):
    pass


class TabConnectionException(AioChromeException):
    pass


class CallMethodException(AioChromeException):
    pass


class TimeoutException(AioChromeException):
    pass


class RuntimeException(AioChromeException):
    pass