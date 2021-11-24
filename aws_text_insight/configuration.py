# -*- coding: utf-8 -*-

"""
App config declaration. (Don't initialize app config object in this module)
"""

import attr
from attrs_mate import AttrsClass
from .helpers import join_s3_uri


@attr.s(auto_attribs=True)
class Configuration(AttrsClass):
    s3_bucket_landing: str
    s3_prefix_landing: str
    s3_bucket_source: str
    s3_prefix_source: str
    s3_bucket_text: str
    s3_prefix_text: str
    s3_bucket_data: str
    s3_prefix_data: str

    def s3_key_source(self, etag):
        return f"{self.s3_prefix_source}/{etag}.file"

    def s3_uri_source(self, etag):
        return join_s3_uri(self.s3_bucket_source, self.s3_key_source(etag))

    def s3_key_text(self, etag):
        return f"{self.s3_prefix_text}/{etag}.text"

    def s3_uri_text(self, etag):
        return join_s3_uri(self.s3_bucket_text, self.s3_key_text(etag))

    def s3_key_data(self, etag):
        return f"{self.s3_prefix_data}/{etag}.json"

    def s3_uri_data(self, etag):
        return join_s3_uri(self.s3_bucket_data, self.s3_key_data(etag))
