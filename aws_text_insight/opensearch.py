# -*- coding: utf-8 -*-

"""
This module manages OpenSearch connections
"""

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def create_connection(
    boto_ses,
    aws_region: str,
    es_endpoint: str,
) -> OpenSearch:
    credentials = boto_ses.get_credentials()
    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        aws_region,
        "es",
        session_token=credentials.token,
    )
    es = OpenSearch(
        hosts=[{"host": es_endpoint, "port": 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return es


def initialize_docs_index(connection: OpenSearch, index_name: str):
    """
    Initialize the documents OpenSearch index.

    1. create index with default settings if not exists
    2. put initial version of mappings
    """
    initial_mapping = {
        "properties": {
            "entities": {
                "properties": {
                    "Type": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "Text": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    }
                }
            },
            "text": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword", "ignore_above": 256}
                }
            }
        }
    }
    try:
        connection.indices.get(index=index_name)
    except:
        connection.indices.create(index=index_name)

    res = connection.indices.get_mapping(index=index_name)
    if len(res[index_name]["mappings"]) == 0:
        connection.indices.put_mapping(index=index_name, body=initial_mapping)
