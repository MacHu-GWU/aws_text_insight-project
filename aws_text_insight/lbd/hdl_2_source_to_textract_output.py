# -*- coding: utf-8 -*-

import traceback
from .event import S3PutEvent
from .logger import logger
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_boto_ses, lbd_s3_client
from ..dynamodb import File
from ..fstate import FileStateEnum
from ..helpers import join_s3_uri
from ..ftype import FileTypeEnum
from ..cf.per_stage_stack import PerStageStack

lbd_tx_client = lbd_boto_ses.client("textract")
stack = PerStageStack(config=config)


def _handler_text(etag: str, file: File):
    try:
        # for pure text file, just copy to the new location
        s3_bucket_input = config.s3_bucket_2_source
        s3_key_input = config.s3_key_2_source(etag=etag)
        s3_bucket_output = config.s3_bucket_4_text
        s3_key_output = config.s3_key_4_text(etag=etag)
        lbd_s3_client.copy_object(
            Bucket=s3_bucket_output,
            Key=s3_key_output,
            CopySource=dict(
                Bucket=s3_bucket_input,
                Key=s3_key_input,
            )
        )
        # update file state
        file.update(
            actions=[
                File.state.set(FileStateEnum.s4_text.value),
            ]
        )
        return Response(
            message="success",
            data=dict(
                s3_input=join_s3_uri(s3_bucket_input, s3_key_input),
                s3_output=join_s3_uri(s3_bucket_output, s3_key_output),
            )
        ).to_dict()
    except:
        # update file state
        file.update(
            actions=[
                File.state.set(FileStateEnum.s2_source_to_text_error.value),
            ]
        )
        return Response(
            message="failed to copy pure text file to new s3 location!",
            error=Error(
                traceback=traceback.format_exc(),
            )
        ).to_dict()


def _handler_pdf_image(etag: str, file: File):
    try:
        # run textract_client.start_document_text_detection()
        s3_bucket_input = config.s3_bucket_2_source
        s3_key_input = config.s3_key_2_source(etag)
        s3_bucket_output = config.s3_bucket_3_textract_output
        s3_prefix_output = f"{config.s3_prefix_3_textract_output}/{etag}"

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
            ),
            JobTag=etag,
            NotificationChannel=dict(
                SNSTopicArn=stack.get_output_value(
                    boto_ses=lbd_boto_ses,
                    output_id=stack.output_sns_topic_arn.id,
                ),
                RoleArn=stack.get_output_value(
                    boto_ses=lbd_boto_ses,
                    output_id=stack.output_iam_role_textract_arn.id,
                ),
            )
        )
        # update file state
        file.update(
            actions=[
                File.state.set(FileStateEnum.s2_textract_async_invoke_processing.value),
            ]
        )
        return Response(
            message="success",
            data=dict(
                s3_input=join_s3_uri(s3_bucket_input, s3_key_input),
                s3_output=join_s3_uri(s3_bucket_output, s3_prefix_output),
            )
        ).to_dict()
    except:
        # update file state
        file.update(
            actions=[
                File.state.set(FileStateEnum.s2_textract_async_invoke_failed.value),
            ]
        )
        return Response(
            message="failed to invoke textract async API!",
            error=Error(
                traceback=traceback.format_exc(),
            )
        ).to_dict()


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
            message="not a valid state todo",
            error=Error(
                traceback="not a valid state todo",
            )
        ).to_dict()

    if file.type == FileTypeEnum.text.value:
        return _handler_text(etag, file)
    elif file.type in [FileTypeEnum.pdf.value, FileTypeEnum.image.value]:
        return _handler_pdf_image(etag, file)
    else:
        return Response(
            message="failed to talk to DynamoDB",
            error=Error(
                traceback=traceback.format_exc(),
            ),
        ).to_dict()


def handler(event, context):
    env = S3PutEvent(**event)
    rec = env.Records[0]
    basename = rec.s3.object.key.split("/")[-1]
    etag = basename.split(".")[0]
    response = _handler(etag=etag)
    logger.info(f"response: {response}")
    return response
