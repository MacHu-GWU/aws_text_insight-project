# -*- coding: utf-8 -*-

import enum
import pynamodb
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute


class FileStateEnum(enum.Enum):
    s1_landing = 100
    # failed to copy / rename from landing to source
    s1_landing_to_source_error = 150

    s2_source = 200
    # failed to convert a pure text source to comprehend ready text
    s2_source_to_text_error = 250
    # failed to invoke the async textract API
    s2_textract_async_invoke_failed = 260
    # successfully invoke the async textract API
    s2_textract_async_invoke_processing = 270

    s3_textract_output = 300
    # SNS notification callback lambda function failed
    s3_textract_output_to_text_error = 350

    s4_text = 400
    # failed to invoke the async comprehend API
    s4_comprehend_async_invoke_failed = 460
    # successfully invoke the async comprehend API
    s4_comprehend_async_invoke_processing = 470
    # successfully invoke the async comprehend API, but processing failed
    s4_comprehend_processing_failed = 480

    s5_comprehend_output = 500
    # failed to merge the comprehend output to single json file
    s5_comprehend_output_to_entity_error = 550

    s6_entity = 600
    s6_opensearch_load_failed = 650

    s7_opensearch = 700


class File(Model):
    class Meta:
        table_name = None  # will be decided based on current stage later
        region = "us-east-1"
        billing_mode = pynamodb.models.PAY_PER_REQUEST_BILLING_MODE

    # define attributes
    etag: str = UnicodeAttribute(hash_key=True)
    state: int = NumberAttribute()
    md5: str = UnicodeAttribute()
    s3_uri_landing: str = UnicodeAttribute()
    type: str = UnicodeAttribute()
