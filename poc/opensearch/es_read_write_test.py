# -*- coding: utf-8 -*-

"""
Test OpenSearch read write performance with large text file
"""

import boto3
import json
from rich import print
from pathlib_mate import Path
import opensearchpy.exceptions
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from aws_text_insight.boto_ses import lbd_boto_ses, dev_boto_ses
from aws_text_insight.opensearch import create_connection


# boto_ses = boto3.session.Session()
boto_ses = lbd_boto_ses
print(boto_ses.client("sts").get_caller_identity())
aws_region = "us-east-1"
es_endpoint = "search-public-no-grained-control-ufwufpla4i23iii4ghrfalz5b4.us-east-1.es.amazonaws.com"
es = create_connection(
    boto_ses=boto_ses,
    aws_region=aws_region,
    es_endpoint=es_endpoint,
)
# print(es.info())

p = Path("/Users/sanhehu/Documents/GitHub/aws_text_insight-project/poc/comprehend/multiple-files/US-Credit-Markets-COVID-19-Report.txt")
#
body = {
    "text": p.read_text(),
    "entities": [{'BeginOffset': 106, 'EndOffset': 132, 'Score': 0.9653251555189698, 'Text': '24th day of\nJanuary\n,\n2030', 'Type': 'DATE'}, {'BeginOffset': 160, 'EndOffset': 169, 'Score': 0.9983829018880386, 'Text': 'Jake Todd', 'Type': 'PERSON'}, {'BeginOffset': 197, 'EndOffset': 217, 'Score': 0.9229577767280499, 'Text': '123 Property Manager', 'Type': 'ORGANIZATION'}, {'BeginOffset': 218, 'EndOffset': 249, 'Score': 0.8567289263897412, 'Text': 'Rd, San Diego, California 91932', 'Type': 'LOCATION'}, {'BeginOffset': 284, 'EndOffset': 300, 'Score': 0.98866054894664, 'Text': 'Benjamin Jameson', 'Type': 'PERSON'}, {'BeginOffset': 340, 'EndOffset': 344, 'Score': 0.9294985248074703, 'Text': 'each', 'Type': 'QUANTITY'}, {'BeginOffset': 477, 'EndOffset': 519, 'Score': 0.9899764815686235, 'Text': '123 Tenant St, San Diego, California 91932', 'Type': 'LOCATION'}, {'BeginOffset': 639, 'EndOffset': 665, 'Score': 0.9485319454340235, 'Text': '1st day of February\n, 2030', 'Type': 'DATE'}, {'BeginOffset': 681, 'EndOffset': 707, 'Score': 0.9723245027490955, 'Text': '1st day\nof February\n,\n2031', 'Type': 'DATE'}, {'BeginOffset': 784, 'EndOffset': 789, 'Score': 0.9985661847929982, 'Text': '$1400', 'Type': 'QUANTITY'}, {'BeginOffset': 829, 'EndOffset': 830, 'Score': 0.8778597207625694, 'Text': '1', 'Type': 'QUANTITY'}, {'BeginOffset': 834, 'EndOffset': 845, 'Score': 0.6922716408379768, 'Text': 'every month', 'Type': 'QUANTITY'}, {'BeginOffset': 1008, 'EndOffset': 1013, 'Score': 0.9978350371691681, 'Text': '$1400', 'Type': 'QUANTITY'}, {'BeginOffset': 1164, 'EndOffset': 1171, 'Score': 0.9603679219115455, 'Text': '21 days', 'Type': 'QUANTITY'}, {'BeginOffset': 1285, 'EndOffset': 1294, 'Score': 0.9976029336774763, 'Text': 'Jale Ford', 'Type': 'PERSON'}, {'BeginOffset': 1301, 'EndOffset': 1311, 'Score': 0.9905935858184, 'Text': '01/24/2030', 'Type': 'DATE'}, {'BeginOffset': 1350, 'EndOffset': 1360, 'Score': 0.9904103164251702, 'Text': '01/24/2030', 'Type': 'DATE'}, {'BeginOffset': 1375, 'EndOffset': 1391, 'Score': 0.9713704378397827, 'Text': 'Benjamin Jameson', 'Type': 'PERSON'}, {'BeginOffset': 1436, 'EndOffset': 1442, 'Score': 0.6925730317590794, 'Text': 'Page 1', 'Type': 'QUANTITY'}, {'BeginOffset': 1446, 'EndOffset': 1447, 'Score': 0.5178928974687599, 'Text': '1', 'Type': 'QUANTITY'}],
    "user_entered": {
        "ic": {
            "ssn": "123-456-7890"
        }
    }
}
res = es.index(index="my_docs_1", id="1", body=body)

def full_text_search():
    body = {
        "query": {
            "match": {
                "text": "Investment"
            }
        }
    }
    res = es.search(index="docs", body=body)
    print(res["hits"]["hits"][0]["_id"])

full_text_search()
