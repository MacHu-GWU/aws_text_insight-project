# -*- coding: utf-8 -*-


import traceback
from .event import S3PutEvent
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_s3_client
from ..dynamodb import File
from ..fstate import FileStateEnum
from ..helpers import join_s3_uri
from ..ftype import FileTypeEnum, detect_file_type

traceback_msg = traceback.format_exc()


def _handler(bucket, key, etag):
    # create an item in DynamoDB
    try:
        file = File.get(etag)
    except File.DoesNotExist:
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

    if file.state == FileStateEnum.s1_landing.value:
        try:
            file_type = detect_file_type(key)

            # relocate s3 object
            lbd_s3_client.copy_object(
                Bucket=config.s3_bucket_source,
                Key=config.s3_key_source(etag=file.etag),
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
                    s3_output=config.s3_uri_source(etag=file.etag),
                ),
            ).to_dict()
        except Exception as e:
            return Response(
                message="s3 copy object failed or dynamodb update failed",
                error=Error(
                    traceback=traceback.format_exc(),
                ),
            ).to_dict()
    else:
        return Response(
            message="already did!",
            data=dict(
                s3_input=join_s3_uri(bucket, key),
                s3_output=config.s3_uri_source(etag=file.etag),
            ),
        ).to_dict()


def handler(event, context):
    env = S3PutEvent(**event)
    rec = env.Records[0]
    return _handler(
        bucket=rec.s3.bucket.name,
        key=rec.s3.object.key,
        etag=rec.s3.object.eTag,
    )
