# -*- coding: utf-8 -*-

import pytest
from aws_text_insight.lbd.hdl_relocate import _handler, config, lbd_s3_client, File
from aws_text_insight.tests.files import EtagEnum


def test_handler():
    File.get(EtagEnum.file_txt.value).delete()

    response = _handler(
        bucket=config.s3_bucket_landing,
        key=f"{config.s3_prefix_landing}/file.txt",
        etag=EtagEnum.file_txt.value,
    )
    assert response["data"] is not None

    response = lbd_s3_client.head_object(
        Bucket=config.s3_bucket_source,
        Key=f"{config.s3_prefix_source}/{EtagEnum.file_txt.value}.file",
    )
    assert response["ETag"][1:-1] == EtagEnum.file_txt.value


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
