# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path
from aws_text_insight.lbd.hdl_1_landing_to_source import (
    _handler, config, lbd_s3_client,
    File, FileStateEnum, FileTypeEnum,
)
from aws_text_insight.tests.files import EtagEnum
from aws_text_insight.helpers import s3_delete_if_exists

dir_tests = Path(__file__).parent.parent


def test_handler_text_type():
    etag = EtagEnum.file_txt.value

    # prepare s3 object, dynamodb item
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_1_landing,
        key=config.s3_key_2_source(etag=etag),
    )

    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "landing", "file.txt").abspath,
        Bucket=config.s3_bucket_1_landing,
        Key=f"{config.s3_prefix_1_landing}/file.txt",
    )

    File(etag=etag).delete()

    # invoke handler
    response = _handler(
        bucket=config.s3_bucket_1_landing,
        key=f"{config.s3_prefix_1_landing}/file.txt",
        etag=etag,
    )
    assert response["data"] is not None

    # check if the normalized file exists in source prefix
    response = lbd_s3_client.head_object(
        Bucket=config.s3_bucket_2_source,
        Key=config.s3_key_2_source(etag=etag),
    )
    assert response["ETag"][1:-1] == etag

    file = File.get(etag)
    assert file.state == FileStateEnum.s2_source.value
    assert file.type == FileTypeEnum.text.value


def test_handler_image_type():
    etag = EtagEnum.lease_png.value

    # prepare s3 object, dynamodb item
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_1_landing,
        key=config.s3_key_2_source(etag=etag),
    )

    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "landing", "lease.png").abspath,
        Bucket=config.s3_bucket_1_landing,
        Key=f"{config.s3_prefix_1_landing}/lease.png",
    )

    File(etag=etag).delete()

    # invoke handler
    response = _handler(
        bucket=config.s3_bucket_1_landing,
        key=f"{config.s3_prefix_1_landing}/lease.png",
        etag=etag,
    )
    assert response["data"] is not None

    # check if the normalized file exists in source prefix
    response = lbd_s3_client.head_object(
        Bucket=config.s3_bucket_2_source,
        Key=config.s3_key_2_source(etag=etag),
    )
    assert response["ETag"][1:-1] == etag

    file = File.get(etag)
    assert file.state == FileStateEnum.s2_source.value
    assert file.type == FileTypeEnum.image.value


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
