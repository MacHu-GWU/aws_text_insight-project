# -*- coding: utf-8 -*-

"""
CloudFormation template for shared AWS Resource.
dev, test, prod environment will share these Resources.
"""

import attr
import typing
import cottonformation as cf
from cottonformation.res import s3, iam, sns
from ..config_init import Configuration


def to_camel_case(text: str) -> str:
    return text.title().replace("-", "").replace("_", "")


@attr.s
class PerStageStack(cf.Stack):
    config: Configuration = attr.ib()

    @property
    def stack_name(self):
        """
        CloudFormation stack name.
        """
        return self.config.cf_stack_name

    def mk_rg1_s3_buckets(self):
        self.rg1_s3_buckets = cf.ResourceGroup("rg1_s3_buckets")

        s3_bucket_name_list = [
            self.config.s3_bucket_1_landing,
            self.config.s3_bucket_2_source,
            self.config.s3_bucket_4_text,
            self.config.s3_bucket_6_entity,
        ]
        s3_bucket_name_list = list(set(s3_bucket_name_list))
        self.s3_bucket_list: typing.List[s3.Bucket] = list()
        for bucket_name in s3_bucket_name_list:
            s3_bucket = s3.Bucket(
                f"S3Bucket{to_camel_case(bucket_name)}",
                p_BucketName=bucket_name
            )
            self.rg1_s3_buckets.add(s3_bucket)

    def mk_rg2_iam_rols(self):
        self.rg2_iam_roles = cf.ResourceGroup("rg2_iam_roles")

        _principal = {
            "Service": "lambda.amazonaws.com"
        }
        if self.config.stage != "prod":
            _principal["AWS"] = "arn:aws:iam::669508176277:root"

        self.iam_role_lbd = iam.Role(
            "IamRoleForLambdaExecution",
            p_RoleName=f"{self.config.env_name}-lambda-execution",
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
        self.rg2_iam_roles.add(self.iam_role_lbd)

        self.output_iam_role_lbd_arn = cf.Output(
            "IamRoleLbdArn",
            Value=self.iam_role_lbd.rv_Arn,
        )
        self.rg2_iam_roles.add(self.output_iam_role_lbd_arn)

        self.iam_role_textract = iam.Role(
            "IamRoleForTextract",
            p_RoleName=f"{self.config.env_name}-textract",
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
        self.rg2_iam_roles.add(self.iam_role_textract)
        self.output_iam_role_textract_arn = cf.Output(
            "IamRoleTextractArn",
            Value=self.iam_role_textract.rv_Arn,
        )
        self.rg2_iam_roles.add(self.output_iam_role_textract_arn)

        self.iam_role_comprehend = iam.Role(
            "IamRoleForComprehend",
            p_RoleName=f"{self.config.env_name}-comprehend",
            rp_AssumeRolePolicyDocument={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "comprehend.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            p_ManagedPolicyArns=[
                cf.helpers.iam.AwsManagedPolicy.AdministratorAccess,
            ],
        )
        self.rg2_iam_roles.add(self.iam_role_comprehend)
        self.output_iam_role_comprehend_arn = cf.Output(
            "IamRoleComprehendArn",
            Value=self.iam_role_comprehend.rv_Arn,
        )
        self.rg2_iam_roles.add(self.output_iam_role_comprehend_arn)

    def mk_rg3_sns_topic(self):
        self.rg3_sns_topic = cf.ResourceGroup("rg3_sns_topics")

        self.sns_topic = sns.Topic(
            "SNSTopic",
            p_TopicName=f"{self.config.env_name}-textract",
            p_FifoTopic=False,
        )
        self.rg3_sns_topic.add(self.sns_topic)

        self.output_sns_topic_arn = cf.Output(
            "SNSTopicArn",
            Description="SNS Topic Arn",
            Value=self.sns_topic.ref(),
        )
        self.rg3_sns_topic.add(self.output_sns_topic_arn)

    def post_hook(self):
        """
        A user custom post stack initialization hook function. Will be executed
        after object initialization.

        We will put all resources in two different resource group.
        And there will be a factory method for each resource group. Of course
        we have to explicitly call it to create those resources.
        """
        self.mk_rg1_s3_buckets()
        self.mk_rg2_iam_rols()
        self.mk_rg3_sns_topic()
