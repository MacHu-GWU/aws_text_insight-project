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
from aws_text_insight.lbd.logger import logger
from aws_text_insight.lbd import (
    hdl_1_landing_to_source,
    hdl_2_source_to_textract_output,
    hdl_3_textract_output_to_text,
    hdl_4_text_to_comprehend_output,
    hdl_5_comprehend_output_to_entity,
)
from aws_text_insight.boto_ses import lbd_boto_ses
from aws_text_insight.cf.per_stage_stack import PerStageStack

app = Chalice(app_name=config.project_name_slugify)

stack = PerStageStack(config=config)


@app.on_s3_event(
    bucket=config.s3_bucket_1_landing,
    prefix=config.s3_prefix_1_landing,
    events=["s3:ObjectCreated:*", ],
    name=f"landing_to_source",
)
def landing_to_source(event: S3Event):
    logger.info(str(event.to_dict()))
    return hdl_1_landing_to_source.handler(event.to_dict(), event.context)


@app.on_s3_event(
    bucket=config.s3_bucket_2_source,
    prefix=config.s3_prefix_2_source,
    suffix="file",
    events=["s3:ObjectCreated:*", ],
    name=f"source_to_text",
)
def source_to_text(event: S3Event):
    logger.info(str(event.to_dict()))
    return hdl_2_source_to_textract_output.handler(event.to_dict(), event.context)


@app.on_sns_message(
    topic=stack.get_output_value(
        boto_ses=lbd_boto_ses,
        output_id=stack.output_sns_topic_arn.id,
    ),
    name=f"textract_output_to_text",
)
def textract_output_to_text(event: SNSEvent):
    logger.info(str(event.to_dict()))
    return hdl_3_textract_output_to_text.handler(event.to_dict(), event.context)


@app.on_s3_event(
    bucket=config.s3_bucket_4_text,
    prefix=config.s3_prefix_4_text,
    suffix="text.txt",
    events=["s3:ObjectCreated:*", ],
    name=f"text_to_comprehend_output",
)
def text_to_comprehend_output(event: S3Event):
    logger.info(str(event.to_dict()))
    return hdl_4_text_to_comprehend_output.handler(event.to_dict(), event.context)


@app.on_s3_event(
    bucket=config.s3_bucket_5_comprehend_output,
    prefix=config.s3_prefix_5_comprehend_output,
    suffix="output.tar.gz",
    events=["s3:ObjectCreated:*", ],
    name=f"comprehend_output_to_entity",
)
def comprehend_output_to_entity(event: S3Event):
    logger.info(str(event.to_dict()))
    return hdl_5_comprehend_output_to_entity.handler(event.to_dict(), event.context)
