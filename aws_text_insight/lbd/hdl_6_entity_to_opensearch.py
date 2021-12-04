# -*- coding: utf-8 -*-

import json
import traceback
from .event import S3PutEvent
from .logger import logger
from .response import Response, Error
from ..config_init import config
from ..boto_ses import lbd_boto_ses, lbd_s3_client
from ..dynamodb import File
from ..opensearch import create_connection, initialize_docs_index
from ..fstate import FileStateEnum

es = create_connection(
    boto_ses=lbd_boto_ses,
    aws_region="us-east-1",
    es_endpoint=config.opensearch_endpoint,
)
initialize_docs_index(es, config.opensearch_docs_index_name)


def _handler(etag: str):
    try:
        file = File.get(etag)
    except:
        return Response(
            message="failed to talk to DynamoDB",
            error=Error(
                traceback=traceback.format_exc(),
            ),
        ).to_dict()

    if file.state != FileStateEnum.s6_entity.value:
        return Response(
            message="not a valid state todo",
            error=Error(
                traceback="not a valid state todo",
            )
        ).to_dict()

    try:
        s3_bucket_input_text = config.s3_bucket_4_text
        s3_key_input_text = config.s3_key_4_text(etag=etag)
        s3_bucket_input_entity = config.s3_bucket_6_entity
        s3_key_input_entity = config.s3_key_6_entity(etag=etag)

        text_body = lbd_s3_client.get_object(
            Bucket=s3_bucket_input_text,
            Key=s3_key_input_text,
        )["Body"].read().decode("utf-8")
        entity_data = json.loads(
            lbd_s3_client.get_object(
                Bucket=s3_bucket_input_entity,
                Key=s3_key_input_entity,
            )["Body"].read().decode("utf-8")
        )
        doc_dict = {
            "text": text_body,
            "entities": entity_data,
        }
        es.index(
            index=config.opensearch_docs_index_name,
            id=etag,
            body=doc_dict,
        )
        file.update(
            actions=[
                File.state.set(FileStateEnum.s7_opensearch.value),
            ]
        )
        return Response(
            message="success!",
        ).to_dict()
    except:
        file.update(
            actions=[
                File.state.set(FileStateEnum.s6_opensearch_load_failed.value),
            ]
        )
        return Response(
            message="failed to load documents to opensearch!",
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
