# -*- coding: utf-8 -*-

"""
CloudFormation template for this solution
"""

import attr
from attrs_mate import AttrsClass
import cottonformation as cf
from cottonformation.res import (
    s3, sns, iam,
)
from ..config_init import config


def to_camel_case(text: str) -> str:
    return text.title().replace("-", "").replace("_", "")


@attr.s
class Params(AttrsClass):
    project_name: str = attr.ib()
    stage: str = attr.ib()

    @property
    def project_name_slugify(self):
        return self.project_name.replace("_", "-")

    @property
    def env_name(self):
        return f"{self.project_name_slugify}-{self.stage}"


def create_template(params: Params) -> cf.Template:
    tpl = cf.Template(Description=f"stack for {params.stage}")

    s3_bucket_name_list = [
        config.s3_bucket_1_landing,
        config.s3_bucket_2_source,
        config.s3_bucket_4_text,
        config.s3_bucket_6_entity,
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
        ProjectName=params.project_name_slugify,
        EnvName=params.env_name,
        Stage=params.stage,
    )

    return tpl
