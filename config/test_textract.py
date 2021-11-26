# -*- coding: utf-8 -*-

from aws_text_insight.boto_ses import lbd_boto_ses
from aws_text_insight.tests.files import EtagEnum
from aws_text_insight.config_init import config

tx_client = lbd_boto_ses.client("textract")

etag = EtagEnum.lease_png.name

s3_bucket = "aws-data-lab-sanhe-text-insight-dev"
s3_key_input = "landing/lease.png"
s3_key_output = f"text/lease.png"
tx_client.start_document_text_detection(
    DocumentLocation=dict(
        S3Object=dict(
            Bucket=s3_bucket,
            Name=s3_key_input,
        ),
    ),
    OutputConfig=dict(
        S3Bucket=s3_bucket,
        S3Prefix=s3_key_output,
    ),
    NotificationChannel=dict(
        SNSTopicArn="arn:aws:sns:us-east-1:669508176277:textract-test",
        RoleArn="arn:aws:iam::669508176277:role/aws-text-insight-dev-textract"
    )
)


