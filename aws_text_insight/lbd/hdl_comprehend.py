# -*- coding: utf-8 -*-

import json
import traceback
from .event import S3PutEvent
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_s3_client, lbd_ch_client
from ..dynamodb import File
from ..fstate import FileStateEnum


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
            Bucket=config.s3_bucket_text,
            Key=config.s3_key_text(etag=etag)
        )
        text = get_obj_response["Body"].read().decode("utf-8")

        # detect entity
        detect_entity_response = lbd_ch_client.detect_entities(
            Text=text,
            LanguageCode="en",
        )

        # write entity to s3
        lbd_s3_client.put_object(
            Bucket=config.s3_bucket_entity,
            Key=config.s3_key_entity(etag=etag),
            Body=json.dumps(detect_entity_response)
        )

        # update dynamodb
        file.update(
            actions=[
                File.state.set(FileStateEnum.s5_data.value),
            ]
        )

        return Response(
            message="success!",
            data=dict(
                s3_input=config.s3_uri_text(etag=etag),
                s3_output=config.s3_uri_source(etag=etag),
            ),
        ).to_dict()
    except:
        file.update(
            actions=[
                File.state.set(FileStateEnum.s4_text_to_data_error.value),
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
    return _handler(etag=rec.s3.object.eTag)
