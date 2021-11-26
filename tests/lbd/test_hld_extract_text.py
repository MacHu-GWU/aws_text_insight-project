# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path
from aws_text_insight.lbd.hdl_extract_text import (
    _handler, config, lbd_s3_client,
    File, FileStateEnum, FileTypeEnum,
)
from aws_text_insight.tests.files import EtagEnum

dir_tests = Path(__file__).parent.parent


def test_handler_text_type():
    etag = EtagEnum.file_txt.value

    # prepare s3 object, dynamodb item
    lbd_s3_client.delete_object(
        Bucket=config.s3_bucket_text,
        Key=config.s3_key_text(etag=etag),
    )

    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "file.txt").abspath,
        Bucket=config.s3_bucket_source,
        Key=config.s3_key_source(etag=etag),
    )

    file = File(
        etag=etag, state=FileStateEnum.s2_source.value, type=FileTypeEnum.text.value,
        md5="", s3_uri_landing="",
    )
    file.save()

    # invoke handler
    response = _handler(etag=etag)
    assert response["error"] is None

    # output text.txt file exists
    _ = lbd_s3_client.head_object(
        Bucket=config.s3_bucket_text,
        Key=config.s3_key_text(etag=etag),
    )

    file.refresh()
    assert file.state == FileStateEnum.s4_text.value


def test_handler_image_type():
    etag = EtagEnum.lease_png.value

    # prepare s3 object, dynamodb item
    lbd_s3_client.delete_object(
        Bucket=config.s3_bucket_text,
        Key=config.s3_key_text(etag=etag),
    )

    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "lease.png").abspath,
        Bucket=config.s3_bucket_source,
        Key=config.s3_key_source(etag=etag),
    )

    file = File(
        etag=etag, state=FileStateEnum.s2_source.value, type=FileTypeEnum.image.value,
        md5="", s3_uri_landing="",
    )
    file.save()

    # invoke handler
    response = _handler(etag=etag)
    assert response["error"] is None

    file.refresh()
    assert file.state == FileStateEnum.s3_source_to_textract_processing.value


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
