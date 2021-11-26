# -*- coding: utf-8 -*-

import json
import traceback
from .event import SNSEvent, TextractEvent
from .logger import logger
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_boto_ses, lbd_s3_client
from ..dynamodb import File
from ..fstate import FileStateEnum

lbd_tx_client = lbd_boto_ses.client("textract")


def merge_textract_result(
    s3_client,
    s3_bucket_input, s3_prefix_input,
    s3_bucket_output, s3_key_output,
):
    """
    Merge multiple textract result output files into one single text file.

    :param s3_client: s3 boto3 client
    :param s3_bucket_input: AWS Textract ``start_document_text_detection`` API
        output s3 bucket
    :param s3_prefix_input: AWS Textract ``start_document_text_detection`` API
        output prefix.
    :param s3_bucket_output: where you want to store the merged txt file
    :param s3_key_output: where you want to store the merged txt file
    """
    ls_obj_response = s3_client.list_objects_v2(
        Bucket=s3_bucket_input, Prefix=s3_prefix_input, MaxKeys=1000
    )
    lines = list()
    for content in ls_obj_response.get("Contents", []):
        s3_key = content["Key"]
        if s3_key.endswith(".s3_access_check"):
            continue
        get_obj_response = s3_client.get_object(
            Bucket=s3_bucket_input, Key=s3_key
        )
        data = json.loads(get_obj_response["Body"].read())
        for block in data["Blocks"]:
            block_type = block["BlockType"]
            text = block["Text"]
            if block_type == "LINE":
                lines.append(text)
    body = "\n".join(lines)
    s3_client.put_object(
        Bucket=s3_bucket_output,
        Key=s3_key_output,
        Body=body,
    )
    return body


def _handler(textract_event):
    etag = textract_event.JobTag
    try:
        file = File.get(etag)
    except:
        return Response(
            message="failed to talk to DynamoDB",
            error=Error(
                traceback=traceback.format_exc(),
            ),
        ).to_dict()

    if file.state != FileStateEnum.s3_source_to_textract_processing.value:
        return Response(
            message="not a valid state todo",
            error=Error(
                traceback="not a valid state todo",
            )
        ).to_dict()

    if textract_event.Status != "SUCCEEDED":
        file.update(
            actions=[
                File.state.set(FileStateEnum.s3_textract_output_to_text_error.value),
            ]
        )
        return Response(
            message="textract processing failed",
            error=Error(
                traceback=f"textract processing failed, etag = {etag} JobId = {textract_event.JobId}",
            )
        ).to_dict()

    try:
        merge_textract_result(
            s3_client=lbd_s3_client,
            s3_bucket_input=config.s3_bucket_text,
            s3_prefix_input=f"{config.s3_prefix_text}/{etag}/{textract_event.JobId}",
            s3_bucket_output=config.s3_bucket_text,
            s3_key_output=config.s3_key_text(etag),
        )
        file.update(
            actions=[
                File.state.set(FileStateEnum.s4_text.value),
            ]
        )
        return Response(
            message="success!",
            data=dict(
                s3_output=config.s3_uri_text(etag),
            ),
        ).to_dict()
    except:
        return Response(
            message="failed to merge textract result",
            error=Error(
                traceback=traceback.format_exc(),
            )
        ).to_dict()


def handler(event, context):
    env = SNSEvent(**event)
    rec = env.Records[0]
    textract_event = TextractEvent(**json.loads(rec.Sns.Message))
    response = _handler(textract_event=textract_event)
    logger.info(f"response: {response}")
    return response