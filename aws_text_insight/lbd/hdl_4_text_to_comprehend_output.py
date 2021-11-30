# -*- coding: utf-8 -*-

import json
import traceback
from .event import S3PutEvent
from .logger import logger
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_s3_client, lbd_ch_client
from ..dynamodb import File
from ..fstate import FileStateEnum
from ..ftype import FileTypeEnum


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
        # read text data
        get_obj_response = lbd_s3_client.get_object(
            Bucket=config.s3_bucket_4_text,
            Key=config.s3_key_4_text(etag=etag)
        )
        text = get_obj_response["Body"].read().decode("utf-8")

        # detect entity
        detect_entity_response = lbd_ch_client.detect_entities(
            Text=text,
            LanguageCode="en",
        )

        # write entity to s3
        lbd_s3_client.put_object(
            Bucket=config.s3_bucket_6_entity,
            Key=config.s3_key_6_entity(etag=etag),
            Body=json.dumps(detect_entity_response)
        )

        # update dynamodb
        file.update(
            actions=[
                File.state.set(FileStateEnum.s5_comprehend_output.value),
            ]
        )

        return Response(
            message="success!",
            data=dict(
                s3_input=config.s3_uri_4_text(etag=etag),
                s3_output=config.s3_uri_6_entity(etag=etag),
            ),
        ).to_dict()
    except:
        file.update(
            actions=[
                File.state.set(FileStateEnum.s4_comprehend_async_invoke_failed.value),
            ]
        )
        return Response(
            message="detect entity or dynamodb update failed",
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
