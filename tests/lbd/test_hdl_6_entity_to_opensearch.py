# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path

from aws_text_insight.config_init import config
from aws_text_insight.boto_ses import lbd_s3_client
from aws_text_insight.ftype import FileTypeEnum
from aws_text_insight.fstate import FileStateEnum
from aws_text_insight.dynamodb import File
from aws_text_insight.helpers import s3_delete_if_exists
from aws_text_insight.tests.files import EtagEnum
from aws_text_insight.lbd.hdl_6_entity_to_opensearch import _handler, es

dir_tests = Path(__file__).parent.parent


def test_handler_good_case():
    # ---------------------------------------------------------------------
    # Begin: prepare before invoke state
    etag = EtagEnum.lease_png.value

    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "text", "png.txt").abspath,
        Bucket=config.s3_bucket_4_text,
        Key=config.s3_key_4_text(etag=etag)
    )
    lbd_s3_client.upload_file(
        Path(dir_tests, "files", "entity", "png", "entity.json").abspath,
        Bucket=config.s3_bucket_6_entity,
        Key=config.s3_key_6_entity(etag=etag)
    )
    file = File(
        etag=etag,
        state=FileStateEnum.s6_entity.value,
        type=FileTypeEnum.pdf.value,
        md5="", s3_uri_landing="",
    )
    file.save()
    # End: prepare before invoke state
    # ---------------------------------------------------------------------
    # --- invoke handler, this one will succeed
    response = _handler(etag=etag)

    # ---------------------------------------------------------------------
    # Begin: validate after invoke state
    file.refresh()
    assert file.state == FileStateEnum.s7_opensearch.value
    res = es.get(index=config.opensearch_docs_index_name, id=etag)
    _ = res["_source"]
    # End: validate after invoke state
    # ---------------------------------------------------------------------


def test_handler_bad_case():
    # ---------------------------------------------------------------------
    # Begin: prepare before invoke state

    # End: prepare before invoke state
    # ---------------------------------------------------------------------
    etag = EtagEnum.lease_pdf.value
    s3_delete_if_exists(lbd_s3_client, bucket=config.s3_bucket_4_text, key=config.s3_key_4_text(etag=etag))

    # --- invoke handler, this one will failed
    response = _handler(etag=etag)

    # ---------------------------------------------------------------------
    # Begin: validate after invoke state
    assert bool(response["error"]) is True
    # End: validate after invoke state
    # ---------------------------------------------------------------------


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
