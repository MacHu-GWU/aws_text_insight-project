# -*- coding: utf-8 -*-

"""
Reference:

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_entities_detection_job
"""

import boto3
from pathlib_mate import Path
from aws_text_insight.fingerprint import fingerprint
from aws_text_insight.helpers import s3_upload_and_md5_rename

boto_ses = boto3.session.Session()
s3_client = boto_ses.client("s3")
cp_client = boto_ses.client("comprehend")

dir_here = Path(__file__).parent
p = Path(dir_here, "Trends-in-the-Expenses-and-Fees-of-Funds-2020.txt")
md5 = fingerprint.of_file(p.abspath)

bucket = "aws-data-lab-sanhe-for-everything"


def start_job():
    response = cp_client.start_entities_detection_job(
        # InputDataConfig=dict(
        #     S3Uri=f"s3://{bucket}/poc/comprehend/single-file/Trends-in-the-Expenses-and-Fees-of-Funds-2020.txt",
        #     InputFormat="ONE_DOC_PER_FILE",
        # ),
        # OutputDataConfig=dict(
        #     S3Uri=f"s3://{bucket}/poc/comprehend/single-file-output"
        # ),
        InputDataConfig=dict(
            S3Uri=f"s3://{bucket}/poc/comprehend/multiple-files/",
            InputFormat="ONE_DOC_PER_FILE",
        ),
        OutputDataConfig=dict(
            S3Uri=f"s3://{bucket}/poc/comprehend/multiple-files-output/"
        ),
        DataAccessRoleArn="arn:aws:iam::669508176277:role/aws-text-insight-dev-comprehend",
        LanguageCode="en",
    )

start_job()

