# -*- coding: utf-8 -*-


import traceback
from .event import S3PutEvent
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_boto_ses, lbd_s3_client
from ..dynamodb import File, FileStateEnum
from ..helpers import join_s3_uri
from ..ftype import FileTypeEnum

lbd_tx_client = lbd_boto_ses.client("textract")


def _handler_text(etag: str, file: File):
    lbd_s3_client.copy_object(
        Bucket=config.s3_bucket_text,
        Key=config.s3_key_text(etag=etag),
        CopySource=dict(
            Bucket=config.s3_bucket_source,
            Key=config.s3_key_source(etag),
        )
    )
    # update DynamoDB item
    file.update(
        actions=[
            File.state.set(FileStateEnum.s4_text.value),
        ]
    )

def _handler_pdf_image(etag: str, file: File):
    # start_document_text_detection()
    s3_bucket_input = config.s3_bucket_source
    s3_key_input = config.s3_key_source(etag)
    s3_bucket_output = config.s3_bucket_text
    s3_prefix_output = f"{config.s3_prefix_text}/{etag}"
    lbd_tx_client.start_document_text_detection(
        DocumentLocation=dict(
            S3Object=dict(
                Bucket=s3_bucket_input,
                Name=s3_key_input,
            ),
        ),
        OutputConfig=dict(
            S3Bucket=s3_bucket_output,
            S3Prefix=s3_prefix_output,
        )
    )

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

    if file.state != FileStateEnum.s2_source.value:
        return Response(
            message="nothing todo ",
            # data=dict(
            #     s3_input=join_s3_uri(bucket, key),
            #     s3_output=config.s3_uri_source(etag=file.etag),
            # ),
        ).to_dict()

    s3_bucket_input = config.s3_bucket_source
    s3_key_input = config.s3_key_source(etag)
    s3_bucket_output = config.s3_bucket_text
    s3_key_output = config.s3_key_text(etag)
    success_response = Response(
        message="success",
        data=dict(
            s3_input=join_s3_uri(s3_bucket_input, s3_key_input),
            s3_output=join_s3_uri(s3_bucket_output, s3_key_output),
        )
    )

    if file.type == FileTypeEnum.text:
        _handler_text(etag, file)
    else:
        _handler_pdf_image(etag, file)

    return success_response

#
#
# def handler(event, context):
#     env = S3PutEvent(**event["Records"][0])
#     return _handler(
#         bucket=env.s3.bucket.name,
#         key=env.s3.object.key,
#         etag=env.s3.object.eTag,
#     )
