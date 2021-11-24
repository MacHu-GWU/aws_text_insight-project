# -*- coding: utf-8 -*-

from .event import S3PutEvent
from ..app_config import config
from ..boto_ses import lbd_s3_client
from ..dynamodb import File, FileState
from ..helpers import join_s3_uri


def _handler(bucket, key, etag):
    # create an item in DynamoDB
    try:
        file = File.get(etag)
    except File.DoesNotExist:
        file = File(
            etag=etag,
            state=FileState.s1_landing.value,
            md5=etag,
            s3_uri_landing=join_s3_uri(bucket, key),
        )
        file.save()
    except:
        raise

    if file.state == FileState.s1_landing.value:
        try:
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
                    File.state.set(FileState.s2_source.value)
                ]
            )
            return {
                "message": "success!",
                "output": config.s3_uri_source(etag=file.etag)
            }
        except Exception as e:
            return {
                "message": "error: {}".format(repr(e)),
                "output": None
            }
    else:
        return {
            "message": "already did!",
            "output": config.s3_uri_source(etag=file.etag)
        }


def handler(event, context):
    env = S3PutEvent(**event["Records"][0])
    return _handler(
        bucket=env.s3.bucket.name,
        key=env.s3.object.key,
        etag=env.s3.object.eTag,
    )
