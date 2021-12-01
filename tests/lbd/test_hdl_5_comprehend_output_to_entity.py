# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path
from aws_text_insight.lbd.hdl_5_comprehend_output_to_entity import (
    _handler, config, lbd_s3_client,
    File, FileStateEnum, FileTypeEnum,
)
from aws_text_insight.lbd.event import TextractDocumentLocation, TextractEvent
from aws_text_insight.tests.files import EtagEnum
from aws_text_insight.helpers import s3_delete_if_exists, s3_is_exists, join_s3_uri

dir_tests = Path(__file__).parent.parent


def test_handler():
    etag = EtagEnum.lease_pdf.value
    job_id = "job_id"

    s3_bucket_input = config.s3_bucket_5_comprehend_output
    s3_key_input = f"{config.s3_prefix_5_comprehend_output}/{etag}/111122223333-NER-{job_id}/output/output.tar.gz"
    s3_bucket_output = config.s3_bucket_6_entity
    s3_key_output = config.s3_key_6_entity(etag=etag)

    # prepare s3 object, dynamodb item
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=s3_bucket_input,
        key=s3_key_input,
    )
    s3_delete_if_exists(
        lbd_s3_client,
        bucket=s3_bucket_output,
        key=s3_key_output,
    )
    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "comprehend_output", "pdf", "output.tar.gz").abspath,
        Bucket=s3_bucket_input,
        Key=s3_key_input,
    )
    file = File(
        etag=etag,
        state=FileStateEnum.s4_comprehend_async_invoke_processing.value,
        type=FileTypeEnum.pdf.value,
        md5="", s3_uri_landing="",
    )
    file.save()

    # invoke handler, this one will fail
    response = _handler(
        etag=etag,
        job_id=job_id,
        _is_test=True,
        _job_status="FAILED",
        _comprehend_output_uri=join_s3_uri(s3_bucket_input, s3_key_input),
    )
    assert response["error"] is not None

    # validate output
    file.refresh()
    assert file.state == FileStateEnum.s4_comprehend_processing_failed.value
    assert s3_is_exists(
        lbd_s3_client,
        bucket=s3_bucket_output,
        key=s3_key_output,
    ) is False

    # invoke handler, this one will succeed
    file.update(
        actions=[
            File.state.set(FileStateEnum.s4_comprehend_async_invoke_processing.value),
        ]
    )
    response = _handler(
        etag=etag,
        job_id=job_id,
        _is_test=True,
        _job_status="COMPLETED",
        _comprehend_output_uri=join_s3_uri(s3_bucket_input, s3_key_input),
    )
    assert response["error"] is None

    # validate output
    file.refresh()
    assert file.state == FileStateEnum.s6_entity.value
    assert s3_is_exists(
        lbd_s3_client,
        bucket=s3_bucket_output,
        key=s3_key_output,
    )


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
