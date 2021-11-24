# -*- coding: utf-8 -*-

import boto3
from .runtime import RuntimeEnum, current_runtime

aws_profile_local_dev = "aws_data_lab_sanhe_assume_role_for_iam_test"


def create_lbd_boto_ses_local():
    return boto3.session.Session(profile_name=aws_profile_local_dev)


def create_lbd_boto_ses_lbd():
    return boto3.session.Session()


_lbd_boto_ses_mapper = {
    RuntimeEnum.local: create_lbd_boto_ses_local,
    RuntimeEnum.lbd: create_lbd_boto_ses_lbd,
}

lbd_boto_ses = _lbd_boto_ses_mapper[current_runtime]()
lbd_s3_client = lbd_boto_ses.client("s3")
