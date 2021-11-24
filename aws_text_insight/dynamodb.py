# -*- coding: utf-8 -*-

from pynamodb.connection import Connection
from .boto_ses import aws_profile_local_dev
from .runtime import RuntimeEnum, current_runtime
from .fstate import FileStateEnum, File


def connect_in_local_runtime() -> Connection:
    import os
    os.environ["AWS_DEFAULT_PROFILE"] = aws_profile_local_dev
    return Connection()


def connect_in_lbd_runtime() -> Connection:
    return Connection()


_mapper = {
    RuntimeEnum.local: connect_in_local_runtime,
    RuntimeEnum.lbd: connect_in_lbd_runtime,
}

connect: Connection = _mapper[current_runtime]()
File.create_table(wait=True)
