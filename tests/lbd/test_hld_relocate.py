# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path
from aws_text_insight.lbd.hdl_relocate import _handler, config, lbd_s3_client, File
from aws_text_insight.tests.files import EtagEnum

dir_tests = Path(__file__).parent.parent


def test_handler():
    # clean up existing s3 object, dynamodb item
    lbd_s3_client.delete_object(
        Bucket=config.s3_bucket_landing,
        Key=config.s3_key_source(etag=EtagEnum.file_txt.value),
    )
    File(etag=EtagEnum.file_txt.value).delete()

    # upload the file in landing prefix
    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "file.txt").abspath,
        Bucket=config.s3_bucket_landing,
        Key=f"{config.s3_prefix_landing}/file.txt",
    )

    # invoke handler
    response = _handler(
        bucket=config.s3_bucket_landing,
        key=f"{config.s3_prefix_landing}/file.txt",
        etag=EtagEnum.file_txt.value,
    )
    assert response["data"] is not None

    # check if the normalized file exists in source prefix
    response = lbd_s3_client.head_object(
        Bucket=config.s3_bucket_source,
        Key=config.s3_key_source(etag=EtagEnum.file_txt.value),
    )
    assert response["ETag"][1:-1] == EtagEnum.file_txt.value


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
