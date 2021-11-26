# -*- coding: utf-8 -*-

import enum
import pynamodb
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute


class FileStateEnum(enum.Enum):
    s1_landing = 100
    s1_landing_to_source_error = 150

    s2_source = 200
    s2_source_to_text_error = 250

    s3_source_to_textract_processing = 260
    s3_source_to_textract_error = 270

    s3_textract_output = 300
    s3_textract_output_to_text_error = 350

    s4_text = 400
    s4_text_to_data_error = 450

    s5_data = 500


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
