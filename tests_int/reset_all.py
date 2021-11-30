# -*- coding: utf-8 -*-

from pathlib_mate import Path
from aws_text_insight.config_init import config
from aws_text_insight.boto_ses import dev_s3_client
from aws_text_insight.dynamodb import File

dir_project_root = Path(__file__).parent.parent


def s3_delete_all_objects():
    res = dev_s3_client.list_objects_v2(
        Bucket=config.s3_bucket_1_landing,
        MaxKeys=1000,
    )
    dev_s3_client.delete_objects(
        Bucket=config.s3_bucket_1_landing,
        Delete=dict(
            Objects=[
                dict(Key=obj["Key"])
                for obj in res["Contents"]
            ]
        )
    )


def dynamodb_delete_all_item():
    with File.batch_write() as batch:
        result = File.scan(attributes_to_get=[File.etag.attr_name, ], limit=1000)
        for item in result:
            batch.delete(item)


def upload_to_landing():
    for p in Path(dir_project_root, "tests", "files", "landing").select_file():
        dev_s3_client.upload_file(
            p.abspath,
            config.s3_bucket_1_landing,
            f"{config.s3_prefix_1_landing}/{p.basename}"
        )


s3_delete_all_objects()
dynamodb_delete_all_item()
# upload_to_landing()
