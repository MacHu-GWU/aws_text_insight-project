# -*- coding: utf-8 -*-

"""
Config initialization
"""

from .runtime import RuntimeEnum, current_runtime
from .config_def import Configuration
from .boto_ses import lbd_boto_ses
from pysecret import AWSSecret


def _local() -> Configuration:
    from .boto_ses import dev_boto_ses
    stage = "dev"
    param_name = f"text_insight_{stage}"
    aws = AWSSecret(boto_session=dev_boto_ses)
    config = aws.get_parameter_object(name=param_name)
    return config


def _lbd() -> Configuration:
    stage = "dev"
    param_name = f"text_insight_{stage}"
    aws = AWSSecret(boto_session=lbd_boto_ses)
    config = aws.get_parameter_object(name=param_name)
    return config


def load_config() -> Configuration:
    if current_runtime is RuntimeEnum.local:
        return _local()
    elif current_runtime is RuntimeEnum.lbd:
        return _lbd()
    else:
        raise Exception


config = load_config()
