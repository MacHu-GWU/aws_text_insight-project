# -*- coding: utf-8 -*-

"""
Response object.
"""

import typing
import attr
from attrs_mate import AttrsClass


@attr.s
class Error(AttrsClass):
    traceback: str = attr.ib()


@attr.s
class Response(AttrsClass):
    message: str = attr.ib()
    data: typing.Union[dict, None] = attr.ib(default=None)
    error: typing.Union[Error, None] = Error.ib_nested(default=None)
