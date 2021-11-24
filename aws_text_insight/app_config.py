# -*- coding: utf-8 -*-

from .runtime import RuntimeEnum, current_runtime
from .configuration import Configuration
from .boto_ses import lbd_boto_ses
from pysecret import AWSSecret


def load_config() -> Configuration:
    if current_runtime is RuntimeEnum.lbd:
        stage = "prod"
    elif current_runtime is RuntimeEnum.local:
        stage = "dev"
    else:
        raise Exception
    param_name = f"text_insight_{stage}"
    aws = AWSSecret(boto_session=lbd_boto_ses)
    config = aws.get_parameter_object(name=param_name)
    return config


config = load_config()
