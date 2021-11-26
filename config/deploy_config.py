# -*- coding: utf-8 -*-

from pysecret import AWSSecret
from aws_text_insight.config_def import Configuration


def config_maker(stage, bucket, prefix):
    return Configuration(
        project_name="aws_text_insight",
        stage=stage,
        s3_bucket_landing=f"{bucket}-{stage}",
        s3_prefix_landing=f"{prefix}/landing",
        s3_bucket_source=f"{bucket}-{stage}",
        s3_prefix_source=f"{prefix}/source",
        s3_bucket_text=f"{bucket}-{stage}",
        s3_prefix_text=f"{prefix}/text",
        s3_bucket_data=f"{bucket}-{stage}",
        s3_prefix_data=f"{prefix}/data",
    )


stage = "test"
bucket = "aws-data-lab-sanhe-text-insight"
prefix = "poc"
param_name = f"text_insight_{stage}"

config = config_maker(stage, bucket, prefix)
aws = AWSSecret(profile_name="aws_data_lab_sanhe")
aws.deploy_parameter_object(
    name=param_name,
    parameter_obj=config,
    update_mode=aws.UpdateModeEnum.upsert,
)
