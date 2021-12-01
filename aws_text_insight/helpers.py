# -*- coding: utf-8 -*-

import typing
from .fingerprint import fingerprint


# --- S3
# --- S3 key, url, uri handling
def split_s3_uri(s3_uri: str) -> typing.Tuple[str, str]:
    parts = s3_uri.split("/")
    bucket = parts[2]
    key = "/".join(parts[3:])
    return bucket, key


def join_s3_uri(bucket: str, key: str) -> str:
    return f"s3://{bucket}/{key}"


def make_s3_console_url(bucket: str, prefix: str) -> str:
    if prefix.endswith("/"):
        s3_type = "buckets"
    else:
        s3_type = "object"
    return "https://s3.console.aws.amazon.com/s3/{s3_type}/{bucket}?prefix={prefix}".format(
        s3_type=s3_type,
        bucket=bucket,
        prefix=prefix
    )


def s3_key_join(parts: typing.List[str], is_dir: bool) -> str:
    """
    A human friendly s3 key join function. This func won't work properly if
    double slash exists. For example, "prefix//surfix" will become "prefix/surfix"
    """
    # strip ending "/" and duplicate "//"
    new_parts = list()
    for part in parts:
        new_parts.extend([chunk for chunk in part.split("/") if chunk])
    key = "/".join(new_parts)
    # append the "/" accordingly
    if is_dir:
        return key + "/"
    else:
        return key


# --- user friendly s3 api call
def s3_delete_if_exists(
    s3_client,
    bucket: str = None,
    key: str = None,
    s3_uri: str = None,
    is_dir: bool = False,
) -> None:
    """
    Delete an object or a folder if exists.
    """
    if s3_uri is not None:
        bucket, key = split_s3_uri(s3_uri)

    if is_dir:
        res = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=s3_key_join([key, ], is_dir=True),
            MaxKeys=1000,
        )
        contents = res.get("Contents", [])
        if len(contents):
            s3_client.delete_objects(
                Bucket=bucket,
                Delete=dict(
                    Objects=[
                        dict(Key=content["Key"])
                        for content in contents
                    ]
                ),
            )
    else:
        try:
            s3_client.delete_object(Bucket=bucket, Key=key)
        except:
            pass


def s3_is_exists(
    s3_client,
    bucket: str = None,
    key: str = None,
    s3_uri: str = None
) -> bool:
    """
    Returns a boolean indicator that if a s3 object exists
    """
    if s3_uri is not None:
        bucket, key = split_s3_uri(s3_uri)
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except:
        return False


def s3_upload_and_md5_rename(
    s3_client,
    path: str,
    bucket: str,
    prefix: str,
) -> None:
    md5 = fingerprint.of_file(path)
    s3_client.upload_file(
        path,
        Bucket=bucket,
        Key=s3_key_join(
            parts=[
                prefix, f"{md5}.file"
            ],
            is_dir=False
        )
    )
