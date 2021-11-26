# -*- coding: utf-8 -*-

import enum
import pynamodb
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute


class FileStateEnum(enum.Enum):
    s1_landing = 1
    s2_source = 2
    s3_textract_output = 3
    s4_text = 4
    s5_data = 5


class File(Model):
    class Meta:
        table_name = None # will be decided based on current stage later
        region = "us-east-1"
        billing_mode = pynamodb.models.PAY_PER_REQUEST_BILLING_MODE

    # define attributes
    etag: str = UnicodeAttribute(hash_key=True)
    state: int = NumberAttribute()
    md5: str = UnicodeAttribute()
    s3_uri_landing: str = UnicodeAttribute()
    type: str = UnicodeAttribute()
