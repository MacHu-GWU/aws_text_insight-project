# -*- coding: utf-8 -*-

import io
import json
import tarfile
import traceback
from .event import S3PutEvent
from .logger import logger
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_boto_ses, lbd_s3_client, lbd_ch_client
from ..dynamodb import File
from ..fstate import FileStateEnum
from ..ftype import FileTypeEnum
from ..helpers import split_s3_uri, join_s3_uri, s3_key_join

MINIMAL_SCORE = 0.3


def _handler(
    etag,
    job_id,
    _is_test=False,
    _job_status=None,
    _comprehend_output_uri=None,
):
    try:
        file = File.get(etag)
    except:
        return Response(
            message="failed to talk to DynamoDB",
            error=Error(
                traceback=traceback.format_exc(),
            ),
        ).to_dict()

    if file.state != FileStateEnum.s4_comprehend_async_invoke_processing.value:
        return Response(
            message="not a valid state todo",
            error=Error(
                traceback="not a valid state todo",
            )
        ).to_dict()

    try:
        # get job status and output file URI
        if _is_test:
            job_status = _job_status
        else:
            describe_job_response = lbd_ch_client.describe_entities_detection_job(
                JobId=job_id
            )
            job_status = describe_job_response["EntitiesDetectionJobProperties"]["JobStatus"]
        # the status won't immediately change to Complete after the output.tar.gz file created, so don't use this logic
        # if job_status != "COMPLETED":
        #     # update file state
        #     file.update(
        #         actions=[
        #             File.state.set(FileStateEnum.s4_comprehend_processing_failed.value),
        #         ]
        #     )
        #     return Response(
        #         message="entities detect job failed!",
        #         error=Error(
        #             traceback=f"entities detect job failed! job_id = '{job_id}'",
        #         ),
        #     ).to_dict()

        file.update(
            actions=[
                File.state.set(FileStateEnum.s5_comprehend_output.value),
            ]
        )
        # the output.tar.gz file uri
        if _is_test:
            comprehend_output_uri = _comprehend_output_uri
        else:
            comprehend_output_uri = describe_job_response \
                ["EntitiesDetectionJobProperties"]["OutputDataConfig"]["S3Uri"]
        s3_bucket_input, s3_key_input = split_s3_uri(comprehend_output_uri)
        s3_bucket_output = config.s3_bucket_6_entity
        s3_key_output = config.s3_key_6_entity(etag=etag)

        res = lbd_s3_client.get_object(Bucket=s3_bucket_input, Key=s3_key_input)
        body = res["Body"].read()
        fileobj = io.BytesIO(body)
        comprehend_output_data = None
        with tarfile.open(fileobj=fileobj) as tar:
            for member in tar:
                comprehend_output_data = json.load(tar.extractfile(member))
                break
        if comprehend_output_data is None:
            return Response(
                message="failed to parse entity data from comprehend output!",
                error=Error(
                    traceback=f"failed to parse entity data from comprehend output",
                ),
            ).to_dict()

        # Convert AWS Comprehend detect entities output to search friendly data
        entity_data = comprehend_output_data.get("Entities", list())

        # store search friendly data to S3
        lbd_s3_client.put_object(
            Bucket=s3_bucket_output,
            Key=s3_key_output,
            Body=json.dumps(entity_data)
        )
        # update file state
        file.update(
            actions=[
                File.state.set(FileStateEnum.s6_entity.value),
            ]
        )
        return Response(
            message="success!",
            data=dict(
                s3_input=comprehend_output_uri,
                s3_output=config.s3_uri_6_entity(etag=etag),
            ),
        ).to_dict()
    except:
        file.update(
            actions=[
                File.state.set(FileStateEnum.s5_comprehend_output_to_entity_error.value),
            ]
        )
        return Response(
            message="failed to transform to entity data",
            error=Error(
                traceback=traceback.format_exc(),
            ),
        ).to_dict()


def handler(event, context):
    env = S3PutEvent(**event)
    rec = env.Records[0]
    s3_key = rec.s3.object.key
    parts = s3_key.split("/")
    etag = parts[-4]
    job_id = parts[-3].split("-")[-1]
    response = _handler(etag=etag, job_id=job_id)
    logger.info(f"response: {response}")
    return response
