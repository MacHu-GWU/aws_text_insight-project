# -*- coding: utf-8 -*-

"""
Reference:

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html#Comprehend.Client.start_entities_detection_job
"""

import boto3
import io
import json
import gzip
from rich import print
from pathlib_mate import Path
from aws_text_insight.fingerprint import fingerprint
from aws_text_insight.helpers import s3_upload_and_md5_rename, split_s3_uri
boto_ses = boto3.session.Session()
s3_client = boto_ses.client("s3")
ch_client = boto_ses.client("comprehend")

dir_here = Path(__file__).parent
p = Path(dir_here, "Trends-in-the-Expenses-and-Fees-of-Funds-2020.txt")
md5 = fingerprint.of_file(p.abspath)

bucket = "aws-data-lab-sanhe-for-everything"


def start_job():
    res = ch_client.start_entities_detection_job(
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


# start_job()


def describe_job():
    res = ch_client.describe_entities_detection_job(
        JobId="9d07c40bca5b36386fa542ce33d50a18"
    )
    print(res)


# describe_job()


def parse_job_output():
    import tarfile

    # p = "/Users/sanhehu/Documents/GitHub/aws_text_insight-project/tests/files/comprehend_output/pdf/output.tar.gz"
    #
    # tar = tarfile.open(p)
    # for m in tar:
    #
    #     s = tar.extractfile(m)
    #     print(json.load(s))
        # print(type(s))



    s3_uri = "s3://aws-data-lab-sanhe-text-insight-dev/poc/comprehend-output/9f724ebab766402cbcbab6ac4f728200/669508176277-NER-9d07c40bca5b36386fa542ce33d50a18/output/output.tar.gz"
    bucket, key = split_s3_uri(s3_uri)
    res = s3_client.get_object(Bucket=bucket, Key=key)
    body = res["Body"].read()
    fileobj = io.BytesIO(body)

    with tarfile.open(fileobj=fileobj) as tar:
        for member in tar:
            entity = json.load(tar.extractfile(member))
            print(entity)
            break
    # with gzip.GzipFile(fileobj=io.BytesIO(body), mode="rb") as f:
    #     print()
    #     data = json.load(f)
    #     print(data)
    # gzipfile = io.BytesIO(body)
    # gzipfile = gzip.GzipFile(fileobj=gzipfile,)
    # content = gzipfile.read().decode("utf-8")
    # print(content)

    # content = gzip.decompress(body).decode("ascii")
    # print([content,])
    # print(type(content))
    # d = json.loads(content)
    # with gzip.GzipFile(fileobj=io.BytesIO(body)) as f:
    #     content = f.read()
    #     print(content)
    #     print(json.loads(content))
    # import zlib
    # json_content = gzip.decompress(res["Body"].read())
    # print(type(json_content))
    # print([json_content,])
    # with gzip.GzipFile(res["Body"]) as f:
    #     print(f.read())

    # s = zlib.decompress(res["Body"].read())
    # print(s)

    # p = "/Users/sanhehu/Documents/GitHub/aws_text_insight-project/tests/files/comprehend_output/pdf/output.tar.gz"
    # with gzip.GzipFile(p, "r") as f:
    #     s = f.read()
    #     print(gzip.decompress(s))
parse_job_output()