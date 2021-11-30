# -*- coding: utf-8 -*-

import time
import pytest
from pathlib_mate import Path
from aws_text_insight.lbd.hdl_2_source_to_textract_output import (
    _handler, config, lbd_s3_client,
    File, FileStateEnum, FileTypeEnum,
)
from aws_text_insight.tests.files import EtagEnum
from aws_text_insight.helpers import s3_delete_if_exists, s3_is_exists

dir_tests = Path(__file__).parent.parent


def test_handler_text_type():
    etag = EtagEnum.file_txt.value

    # prepare s3 object, dynamodb item
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_2_source,
        key=config.s3_key_2_source(etag=etag),
    )
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_4_text,
        key=config.s3_key_4_text(etag=etag),
    )
    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "landing", "file.txt").abspath,
        Bucket=config.s3_bucket_2_source,
        Key=config.s3_key_2_source(etag=etag),
    )
    file = File(
        etag=etag,
        state=FileStateEnum.s2_source.value,
        type=FileTypeEnum.text.value,
        md5="", s3_uri_landing="",
    )
    file.save()

    # invoke handler
    response = _handler(etag=etag)
    assert response["error"] is None

    # output text.txt file exists
    assert s3_is_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_4_text,
        key=config.s3_key_4_text(etag=etag),
    ) is True

    file.refresh()
    assert file.state == FileStateEnum.s4_text.value


def test_handler_image_type():
    etag = EtagEnum.lease_png.value

    # prepare s3 object, dynamodb item
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_2_source,
        key=config.s3_key_2_source(etag=etag),
    )
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_4_text,
        key=f"{config.s3_prefix_3_textract_output}/{etag}",
    )
    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "landing", "lease.png").abspath,
        Bucket=config.s3_bucket_2_source,
        Key=config.s3_key_2_source(etag=etag),
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
    assert file.state == FileStateEnum.s2_textract_async_invoke_processing.value

    res = lbd_s3_client.list_objects_v2(
        Bucket=config.s3_bucket_3_textract_output,
        Prefix=f"{config.s3_prefix_3_textract_output}/{etag}",
    )
    time.sleep(6) # wait a seconds for async textract
    assert len(res.get("Contents", [])) >= 1


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
