# -*- coding: utf-8 -*-


import traceback
from .event import S3PutEvent
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

def _handler_text(etag: str, file: File, success_response: Response):
    try:
        lbd_s3_client.copy_object(
            Bucket=config.s3_bucket_text,
            Key=config.s3_key_text(etag=etag),
            CopySource=dict(
                Bucket=config.s3_bucket_source,
                Key=config.s3_key_source(etag),
            )
        )
    except:
        file.update(
            actions=[
                File.state.set(FileStateEnum.s2_source_to_text_error.value),
            ]
        )
        return Response(
            message="",
            error=Error(
                traceback=traceback.format_exc(),
            )
        ).to_dict()

    # update DynamoDB item
    file.update(
        actions=[
            File.state.set(FileStateEnum.s4_text.value),
        ]
    )
    return success_response.to_dict()


def _handler_pdf_image(etag: str, file: File, success_response: Response):
    try:
        # run textract_client.start_document_text_detection()
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
    except:
        file.update(
            actions=[
                File.state.set(FileStateEnum.s3_source_to_textract_error.value),
            ]
        )
        return Response(
            message="",
            error=Error(
                traceback=traceback.format_exc(),
            )
        ).to_dict()

    # update DynamoDB item
    file.update(
        actions=[
            File.state.set(FileStateEnum.s3_source_to_textract_processing.value),
        ]
    )
    return success_response.to_dict()


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

    if file.type == FileTypeEnum.text.value:
        return _handler_text(etag, file, success_response)
    elif file.type in [FileTypeEnum.pdf.value, FileTypeEnum.image.value]:
        return _handler_pdf_image(etag, file, success_response)
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
    return _handler(etag=etag)
