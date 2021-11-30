# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path
from aws_text_insight.lbd.hdl_3_textract_output_to_text import (
    _handler, config, lbd_s3_client,
    File, FileStateEnum, FileTypeEnum,
)
from aws_text_insight.lbd.event import TextractDocumentLocation, TextractEvent
from aws_text_insight.tests.files import EtagEnum
from aws_text_insight.helpers import s3_delete_if_exists, s3_is_exists

dir_tests = Path(__file__).parent.parent


def test_handler():
    etag = EtagEnum.lease_pdf.value

    # prepare s3 object, dynamodb item
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_3_textract_output,
        key=f"{config.s3_prefix_3_textract_output}/{etag}/job_id/1",
    )
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_4_text,
        key=config.s3_key_4_text(etag=etag),
    )
    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "textract_output", "pdf", "job_id", "1").abspath,
        Bucket=config.s3_bucket_3_textract_output,
        Key=f"{config.s3_prefix_3_textract_output}/{etag}/job_id/1",
    )
    file = File(
        etag=etag,
        state=FileStateEnum.s2_textract_async_invoke_processing.value,
        type=FileTypeEnum.pdf.value,
        md5="", s3_uri_landing="",
    )
    file.save()

    # invoke handler
    textract_event = TextractEvent(
        JobId="job_id",
        Status="SUCCEEDED",
        JobTag=etag,
        API="",
        Timestamp=0,
        DocumentLocation=TextractDocumentLocation(
            S3Bucket="",
            S3ObjectName="",
        ),
    )
    response = _handler(textract_event=textract_event)
    assert response["error"] is None

    # validate output
    file.refresh()
    assert file.state == FileStateEnum.s4_text.value
    assert s3_is_exists(
        lbd_s3_client,
        bucket=config.s3_bucket_4_text,
        key=config.s3_key_4_text(etag=etag),
    )


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
