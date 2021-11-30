# -*- coding: utf-8 -*-

import json
import traceback
from .event import S3PutEvent
from .logger import logger
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_boto_ses, lbd_s3_client, lbd_ch_client
from ..dynamodb import File
from ..fstate import FileStateEnum
from ..ftype import FileTypeEnum
from ..helpers import join_s3_uri, s3_key_join
from ..cf.per_stage_stack import PerStageStack

stack = PerStageStack(config=config)


def _handler(etag):
    try:
        file = File.get(etag)
    except:
        return Response(
            message="failed to talk to DynamoDB",
            error=Error(
                traceback=traceback.format_exc(),
            ),
        ).to_dict()

    if file.state != FileStateEnum.s4_text.value:
        return Response(
            message="not a valid state todo",
            error=Error(
                traceback="not a valid state todo",
            )
        ).to_dict()

    try:
        # run comprehend_client.start_entities_detection_job()
        start_job_response = lbd_ch_client.start_entities_detection_job(
            InputDataConfig=dict(
                S3Uri=config.s3_uri_4_text(etag=etag),
                InputFormat="ONE_DOC_PER_FILE",
            ),
            OutputDataConfig=dict(
                S3Uri=join_s3_uri(
                    config.s3_bucket_5_comprehend_output,
                    f"{config.s3_prefix_5_comprehend_output}/{etag}/",
                ),
            ),
            DataAccessRoleArn=stack.get_output_value(
                boto_ses=lbd_boto_ses,
                output_id=stack.output_iam_role_comprehend_arn.id,
            ),
            LanguageCode="en",
        )
        job_id = start_job_response["JobId"]
        # update file state
        file.update(
            actions=[
                File.state.set(FileStateEnum.s4_comprehend_async_invoke_processing.value),
            ]
        )
        return Response(
            message="success!",
            data=dict(
                s3_input=config.s3_uri_4_text(etag=etag),
                s3_output=join_s3_uri(
                    config.s3_bucket_5_comprehend_output,
                    f"{config.s3_prefix_5_comprehend_output}/{etag}/{job_id}",
                ),
            ),
        ).to_dict()
    except:
        file.update(
            actions=[
                File.state.set(FileStateEnum.s4_comprehend_async_invoke_failed.value),
            ]
        )
        return Response(
            message="failed to invoke comprehend async API!",
            error=Error(
                traceback=traceback.format_exc(),
            ),
        ).to_dict()


def handler(event, context):
    env = S3PutEvent(**event)
    rec = env.Records[0]
    s3_key = rec.s3.object.key
    etag = s3_key.split("/")[-2]
    response = _handler(etag=etag)
    logger.info(f"response: {response}")
    return response
