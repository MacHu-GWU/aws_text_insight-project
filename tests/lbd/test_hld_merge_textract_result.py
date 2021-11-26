# -*- coding: utf-8 -*-

import pytest
from aws_text_insight.lbd.hdl_merge_textract_result import (
    config, lbd_s3_client,
    # File, FileStateEnum, FileTypeEnum,
    merge_textract_result, _handler
)
from aws_text_insight.tests.files import EtagEnum

def test_merge_textract_result():
    etag = EtagEnum.lease_png.value
    merge_textract_result(
        lbd_s3_client,
        config.s3_bucket_text,
        f"{config.s3_prefix_text}/{etag}/dd44bc2f638fcd3501014e04fb8830e342cac8bbbf6df2b09f9992ba69721ab0",
        config.s3_bucket_text,
        config.s3_key_text(etag),
    )




if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
