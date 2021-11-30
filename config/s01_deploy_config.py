# -*- coding: utf-8 -*-

"""
Deploy dev / test / prod configuration to AWS Parameter Store
"""

from pysecret import AWSSecret
from aws_text_insight.config_def import Configuration


def config_maker(stage, bucket, prefix):
    return Configuration(
        project_name="aws_text_insight",
        stage=stage,
        s3_bucket_1_landing=f"{bucket}-{stage}",
        s3_prefix_1_landing=f"{prefix}/landing",
        s3_bucket_2_source=f"{bucket}-{stage}",
        s3_prefix_2_source=f"{prefix}/source",
        s3_bucket_3_textract_output=f"{bucket}-{stage}",
        s3_prefix_3_textract_output=f"{prefix}/textract-output",
        s3_bucket_4_text=f"{bucket}-{stage}",
        s3_prefix_4_text=f"{prefix}/text",
        s3_bucket_5_comprehend_output=f"{bucket}-{stage}",
        s3_prefix_5_comprehend_output=f"{prefix}/comprehend-output",
        s3_bucket_6_entity=f"{bucket}-{stage}",
        s3_prefix_6_entity=f"{prefix}/entity",
    )


stage = "prod"
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
