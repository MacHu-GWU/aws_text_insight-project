# -*- coding: utf-8 -*-

"""
App config definition. (Don't initialize app config object in this module)
"""

import attr
from attrs_mate import AttrsClass
from .helpers import join_s3_uri


@attr.s(auto_attribs=True)
class Configuration(AttrsClass):
    project_name: str
    stage: str
    s3_bucket_landing: str
    s3_prefix_landing: str
    s3_bucket_source: str
    s3_prefix_source: str
    s3_bucket_text: str
    s3_prefix_text: str
    s3_bucket_entity: str
    s3_prefix_entity: str

    @property
    def project_name_slugify(self):
        return self.project_name.replace("_", "-")

    @property
    def env_name(self):
        return f"{self.project_name_slugify}-{self.stage}"

    @property
    def cf_stack_name(self):
        return self.env_name

    def s3_key_source(self, etag):
        return f"{self.s3_prefix_source}/{etag}.file"

    def s3_uri_source(self, etag):
        return join_s3_uri(self.s3_bucket_source, self.s3_key_source(etag))

    def s3_key_text(self, etag):
        return f"{self.s3_prefix_text}/{etag}/text.txt"

    def s3_uri_text(self, etag):
        return join_s3_uri(self.s3_bucket_text, self.s3_key_text(etag))

    def s3_key_entity(self, etag):
        return f"{self.s3_prefix_entity}/{etag}.json"

    def s3_uri_entity(self, etag):
        return join_s3_uri(self.s3_bucket_entity, self.s3_key_entity(etag))
