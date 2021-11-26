# -*- coding: utf-8 -*-

import boto3
from .runtime import RuntimeEnum, current_runtime

aws_profile_lbd_assume_role = "aws_data_lab_sanhe_aws_text_insight_dev"


def create_lbd_boto_ses_local():
    return boto3.session.Session(profile_name=aws_profile_lbd_assume_role)


def create_lbd_boto_ses_lbd():
    return boto3.session.Session()


_lbd_boto_ses_mapper = {
    RuntimeEnum.local: create_lbd_boto_ses_local,
    RuntimeEnum.lbd: create_lbd_boto_ses_lbd,
}

# the boto session object used by AWS Lambda Function
lbd_boto_ses = _lbd_boto_ses_mapper[current_runtime]()
lbd_s3_client = lbd_boto_ses.client("s3")
lbd_tx_client = lbd_boto_ses.client("textract")
lbd_ch_client = lbd_boto_ses.client("comprehend")

# the boto session used by local developer
try:
    dev_boto_ses = boto3.session.Session()
    dev_s3_client = dev_boto_ses.client("s3")
    dev_tx_client = lbd_boto_ses.client("textract")
    dev_ch_client = lbd_boto_ses.client("comprehend")
except:
    pass
