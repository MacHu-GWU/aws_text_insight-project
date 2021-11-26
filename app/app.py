# -*- coding: utf-8 -*-

import os
from chalice import Chalice
from chalice.app import S3Event, SNSEvent

# If we are using chalice to deploy from local.
# it should set the runtime as Lambda runtime
if "AWS_CHALICE_CLI_MODE" in os.environ:
    from aws_text_insight import runtime

    runtime.current_runtime = runtime.RuntimeEnum.lbd

from aws_text_insight.config_init import config
from aws_text_insight.lbd import (
    hdl_relocate,
    hdl_extract_text,
    hdl_merge_textract_result,
)
from aws_text_insight.boto_ses import lbd_boto_ses
from aws_text_insight.cf.per_stage_stack import PerStageStack

app = Chalice(app_name=config.project_name_slugify)

stack = PerStageStack(config=config)

@app.on_s3_event(
    bucket=config.s3_bucket_landing,
    prefix=config.s3_prefix_landing,
    events=["s3:ObjectCreated:*", ],
    name=f"landing_to_source",
)
def landing_to_source(event: S3Event):
    return hdl_relocate.handler(event.to_dict(), event.context)


@app.on_s3_event(
    bucket=config.s3_bucket_landing,
    prefix=config.s3_prefix_source,
    events=["s3:ObjectCreated:*", ],
    name=f"source_to_text",
)
def source_to_text(event: S3Event):
    return hdl_extract_text.handler(event.to_dict(), event.context)


@app.on_sns_message(
    topic=stack.get_output_value(
        boto_ses=lbd_boto_ses,
        output_id=stack.output_sns_topic_arn.id,
    ),
    name=f"textract_output_to_text",
)
def textract_output_to_text(event: SNSEvent):
    return hdl_merge_textract_result.handler(event.to_dict(), event.context)
