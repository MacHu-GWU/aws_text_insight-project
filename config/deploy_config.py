# -*- coding: utf-8 -*-

from pysecret import AWSSecret
from aws_text_insight.configuration import Configuration


def config_maker(bucket, prefix, stage):
    return Configuration(
        s3_bucket_landing=bucket,
        s3_prefix_landing=f"{prefix}/{stage}/landing",
        s3_bucket_source=bucket,
        s3_prefix_source=f"{prefix}/{stage}/source",
        s3_bucket_text=bucket,
        s3_prefix_text=f"{prefix}/{stage}/text",
        s3_bucket_data=bucket,
        s3_prefix_data=f"{prefix}/{stage}/data",
    )


bucket = "aws-data-lab-sanhe-for-everything"
prefix = "poc/2021-11-24-aws_text_insight"
stage = "prod"
param_name = f"text_insight_{stage}"

config = config_maker(bucket, prefix, stage)
aws = AWSSecret(profile_name="aws_data_lab_sanhe")
aws.deploy_parameter_object(
    name=param_name,
    parameter_obj=config,
    update_mode=aws.UpdateModeEnum.upsert,
)
