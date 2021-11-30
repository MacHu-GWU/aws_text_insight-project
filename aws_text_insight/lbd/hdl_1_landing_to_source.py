# -*- coding: utf-8 -*-

"""
Copy file from ``landing`` to ``source``. use ``${etag}.file`` for filename.
"""

import traceback
from .event import S3PutEvent
from .logger import logger
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_s3_client
from ..dynamodb import File
from ..fstate import FileStateEnum
from ..helpers import join_s3_uri
from ..ftype import FileTypeEnum, detect_file_type


def _handler(bucket, key, etag):
    # -- 1. create the initial item in DynamoDB
    try:
        # Do nothing if item already exists
        File.get(etag)
        return Response(
            message="file has been processed already",
            error=Error(
                traceback="file has been processed already",
            ),
        ).to_dict()
    except File.DoesNotExist:
        # Create the initial item if not exists
        file = File(
            etag=etag,
            state=FileStateEnum.s1_landing.value,
            md5=etag,
            s3_uri_landing=join_s3_uri(bucket, key),
            type=FileTypeEnum.unknown.value,
        )
        file.save()
    except:
        return Response(
            message="failed to talk to DynamoDB",
            error=Error(
                traceback=traceback.format_exc(),
            ),
        ).to_dict()

    #--- 2. detect file type, copy file to new location, update dynamodb item
    try:
        # Detect file type
        file_type = detect_file_type(key)

        # relocate s3 object
        lbd_s3_client.copy_object(
            Bucket=config.s3_bucket_2_source,
            Key=config.s3_key_2_source(etag=file.etag),
            CopySource=dict(
                Bucket=bucket,
                Key=key,
            )
        )

        # update DynamoDB item
        file.update(
            actions=[
                File.type.set(file_type.value),
                File.state.set(FileStateEnum.s2_source.value),
            ]
        )

        return Response(
            message="success!",
            data=dict(
                s3_input=join_s3_uri(bucket, key),
                s3_output=config.s3_uri_2_source(etag=file.etag),
            ),
        ).to_dict()
    except:
        file.update(
            actions=[
                File.state.set(FileStateEnum.s1_landing_to_source_error.value),
            ]
        )
        return Response(
            message="s3 copy object failed or dynamodb update failed",
            error=Error(
                traceback=traceback.format_exc(),
            ),
        ).to_dict()


def handler(event, context):
    env = S3PutEvent(**event)
    rec = env.Records[0]
    response = _handler(
        bucket=rec.s3.bucket.name,
        key=rec.s3.object.key,
        etag=rec.s3.object.eTag,
    )
    logger.info(f"response: {response}")
    return response
