# -*- coding: utf-8 -*-

import os
import enum


class RuntimeEnum(enum.Enum):
    local = "local"
    lbd = "lbd"


current_runtime: RuntimeEnum
if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
    current_runtime = RuntimeEnum.lbd
else:
    current_runtime = RuntimeEnum.local
