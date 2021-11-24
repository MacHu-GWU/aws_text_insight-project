# -*- coding: utf-8 -*-

from smart_open import s3
from pathlib_mate import Path
from aws_text_insight.app_config import config
from aws_text_insight.boto_ses import lbd_s3_client

dir_project_root = Path(__file__).parent.parent



def upload_files():
    for p in Path(dir_project_root, "tests", "files").select_file():
        lbd_s3_client.upload_file(
            Filename=p.abspath,
            Bucket=config.s3_bucket_landing,
            Key=f"{config.s3_prefix_landing}/{p.basename}"
        )

def delete_files():
    response = lbd_s3_client.list_objects_v2(
        Bucket=config.s3_bucket_landing,
        Prefix=config.s3_prefix_landing,
    )
    lbd_s3_client.delete_objects(
        Bucket=config.s3_bucket_source,
        Delete=dict(
            Objects=[
                dict(Key=content["Key"])
                for content in response.get("Contents", list())
            ],
            Quiet=True,
        )
    )

upload_files()
# delete_files()
