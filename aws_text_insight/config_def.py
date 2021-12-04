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
    s3_bucket_1_landing: str
    s3_prefix_1_landing: str
    s3_bucket_2_source: str
    s3_prefix_2_source: str
    s3_bucket_3_textract_output: str
    s3_prefix_3_textract_output: str
    s3_bucket_4_text: str
    s3_prefix_4_text: str
    s3_bucket_5_comprehend_output: str
    s3_prefix_5_comprehend_output: str
    s3_bucket_6_entity: str
    s3_prefix_6_entity: str

    opensearch_endpoint: str
    opensearch_docs_index_name: str

    @property
    def project_name_slugify(self):
        return self.project_name.replace("_", "-")

    @property
    def env_name(self):
        return f"{self.project_name_slugify}-{self.stage}"

    @property
    def cf_stack_name(self):
        return self.env_name

    # ---
    def s3_key_2_source(self, etag):
        return f"{self.s3_prefix_2_source}/{etag}/file"

    def s3_uri_2_source(self, etag):
        return join_s3_uri(self.s3_bucket_2_source, self.s3_key_2_source(etag))

    def s3_key_3_textract_output(self, etag):
        raise NotImplemented("This method should NOT be implemented")

    def s3_uri_3_textract_output(self, etag):
        raise NotImplemented("This method should NOT be implemented")

    def s3_key_4_text(self, etag):
        return f"{self.s3_prefix_4_text}/{etag}/text.txt"

    def s3_uri_4_text(self, etag):
        return join_s3_uri(self.s3_bucket_4_text, self.s3_key_4_text(etag))

    def s3_key_5_comprehend_output(self, etag):
        raise NotImplemented("This method should NOT be implemented")

    def s3_uri_5_comprehend_output(self, etag):
        raise NotImplemented("This method should NOT be implemented")

    def s3_key_6_entity(self, etag):
        return f"{self.s3_prefix_6_entity}/{etag}/entity.json"

    def s3_uri_6_entity(self, etag):
        return join_s3_uri(self.s3_bucket_6_entity, self.s3_key_6_entity(etag))
