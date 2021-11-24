# -*- coding: utf-8 -*-

import os
from chalice import Chalice
from chalice.app import S3Event

# If we are using chalice to deploy from local.
# it should set the runtime as Lambda runtime
if "AWS_CHALICE_CLI_MODE" in os.environ:
    from aws_text_insight import runtime

    runtime.current_runtime = runtime.RuntimeEnum.lbd

from aws_text_insight.app_config import config
from aws_text_insight.lbd import (
    hdl_relocate,
)

app = Chalice(app_name="aws_text_insight")


@app.on_s3_event(
    bucket=config.s3_bucket_landing,
    prefix=config.s3_prefix_landing,
    events=["s3:ObjectCreated:*", ],
    name="landing_to_source",
)
def landing_to_source(event: S3Event):
    return hdl_relocate.handler(event.to_dict(), event.context)
