# -*- coding: utf-8 -*-

import typing


# --- S3
def split_s3_uri(s3_uri) -> typing.Tuple[str, str]:
    parts = s3_uri.split("/")
    bucket = parts[2]
    key = "/".join(parts[3:])
    return bucket, key


def join_s3_uri(bucket, key):
    return f"s3://{bucket}/{key}"


def s3_is_exists(s3_client, bucket=None, key=None, s3_uri=None):
    if s3_uri is not None:
        bucket, key = split_s3_uri(s3_uri)
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except:
        return False
