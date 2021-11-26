# -*- coding: utf-8 -*-

"""
CloudFormation template for shared AWS Resource.
dev, test, prod environment will share these Resources.
"""

import cottonformation as cf
from cottonformation.res import s3, iam, sns
from ..config_init import Configuration


def to_camel_case(text: str) -> str:
    return text.title().replace("-", "").replace("_", "")


def create_template(config: Configuration) -> cf.Template:
    tpl = cf.Template(Description=f"shared stack for {config.stage}")

    s3_bucket_name_list = [
        config.s3_bucket_landing,
        config.s3_bucket_source,
        config.s3_bucket_text,
        config.s3_bucket_data,
    ]
    s3_bucket_name_list = list(set(s3_bucket_name_list))

    for bucket_name in s3_bucket_name_list:
        s3_bucket = s3.Bucket(
            f"S3Bucket{to_camel_case(bucket_name)}",
            p_BucketName=bucket_name
        )
        tpl.add(s3_bucket)

    _principal = {
        "Service": "lambda.amazonaws.com"
    }
    if config.stage != "prod":
        _principal["AWS"] = "arn:aws:iam::669508176277:root"

    iam_role_lbd = iam.Role(
        "IamRoleForLambdaExecution",
        p_RoleName=f"{config.env_name}-lambda-execution",
        rp_AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": _principal,
                    "Action": "sts:AssumeRole"
                }
            ]
        },
        p_ManagedPolicyArns=[
            cf.helpers.iam.AwsManagedPolicy.AdministratorAccess,
        ]
    )
    tpl.add(iam_role_lbd)

    iam_role_textract = iam.Role(
        "IamRoleForTextract",
        p_RoleName=f"{config.env_name}-textract",
        rp_AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "textract.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        },
        p_ManagedPolicyArns=[
            cf.helpers.iam.AwsManagedPolicy.AdministratorAccess,
        ],
    )
    tpl.add(iam_role_textract)

    sns_topic = sns.Topic(
        "SNSTopic",
        p_TopicName=f"{config.env_name}-textract",
        p_FifoTopic=False,
    )
    tpl.add(sns_topic)

    tpl.batch_tagging(
        overwrite=True,
        ProjectName=config.project_name_slugify,
        EnvName=config.env_name,
    )

    return tpl
