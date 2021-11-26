# -*- coding: utf-8 -*-

"""
CloudFormation template for shared AWS Resource.
dev, test, prod environment will share these Resources.
"""

import cottonformation as cf
from cottonformation.res import s3
from ..config_init import Configuration


def to_camel_case(text: str) -> str:
    return text.title().replace("-", "").replace("_", "")


def create_template(config: Configuration) -> cf.Template:
    tpl = cf.Template(Description=f"stack for dev, test, prod")

    s3_bucket_name_list = [
        config.s3_bucket_landing,
        config.s3_bucket_source,
        config.s3_bucket_text,
        config.s3_bucket_entity,
    ]
    s3_bucket_name_list = list(set(s3_bucket_name_list))

    for bucket_name in s3_bucket_name_list:
        s3_bucket = s3.Bucket(
            f"S3Bucket{to_camel_case(bucket_name)}",
            p_BucketName=bucket_name
        )
        tpl.add(s3_bucket)

    tpl.batch_tagging(
        overwrite=True,
        ProjectName=config.project_name_slugify,
        EnvName=config.project_name_slugify,
    )

    return tpl
