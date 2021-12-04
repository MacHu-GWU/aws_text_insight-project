# -*- coding: utf-8 -*-

"""
Test the two most important query patterns.
"""

from rich import print
from aws_text_insight.boto_ses import lbd_boto_ses
from aws_text_insight.opensearch import create_connection
from aws_text_insight.tests.files import EtagEnum

boto_ses = lbd_boto_ses
aws_region = "us-east-1"
es_endpoint = "search-public-no-grained-control-ufwufpla4i23iii4ghrfalz5b4.us-east-1.es.amazonaws.com"
es = create_connection(
    boto_ses=boto_ses,
    aws_region=aws_region,
    es_endpoint=es_endpoint,
)


def full_text_search():
    body = {
        "query": {
            "match": {
                "text": "acknowledge"  # should match the pdf file
            }
        }
    }
    res = es.search(index="docs", body=body)
    print(res["hits"]["hits"][0]["_id"])


# full_text_search()


def term_search_by_person():
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "entities.Text": "Benjamin Jameson",
                        }
                    },
                    {
                        "match": {
                            "entities.Type": "PERSON",
                        }
                    },
                ]
            }
        }
    }
    res = es.search(index="docs", body=body)
    print(res["hits"]["hits"][0]["_id"])


# term_search_by_person()

def term_search_by_location():
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "entities.Text": "Tenant St",
                        }
                    },
                    {
                        "match": {
                            "entities.Type": "LOCATION",
                        }
                    },
                ]
            }
        }
    }
    res = es.search(index="docs", body=body)
    print(res["hits"]["hits"][0]["_id"])

# term_search_by_location()
