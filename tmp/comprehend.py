# -*- coding: utf-8 -*-

import json
from aws_text_insight.config_init import config
from aws_text_insight.boto_ses import lbd_boto_ses, lbd_s3_client
from aws_text_insight.tests.files import EtagEnum

cp_client = lbd_boto_ses.client("comprehend")

etag = EtagEnum.lease_png.value
res = lbd_s3_client.get_object(
    Bucket=config.s3_bucket_text,
    Key=config.s3_key_text(etag=etag)
)
text = res["Body"].read().decode("utf-8")
res = cp_client.detect_entities(
    Text=text,
    LanguageCode="en",
)

# print(json.dumps(res, indent=4))
for entity in res.get("Entities", []):
    print(entity)

# {
#     "Entities": [
#         {
#             "Score": 0.961186945438385,
#             "Type": "DATE",
#             "Text": "24th day of\nJanuary\n.\n2030",
#             "BeginOffset": 106,
#             "EndOffset": 132
#         },
#         {
#             "Score": 0.9984322786331177,
#             "Type": "PERSON",
#             "Text": "Jake Todd",
#             "BeginOffset": 160,
#             "EndOffset": 169
#         },
#         {
#             "Score": 0.9251922965049744,
#             "Type": "ORGANIZATION",
#             "Text": "123 Property Manager",
#             "BeginOffset": 197,
#             "EndOffset": 217
#         },
#         {
#             "Score": 0.8471852540969849,
#             "Type": "LOCATION",
#             "Text": "Rd, San Diego, California 91932",
#             "BeginOffset": 218,
#             "EndOffset": 249
#         },
#         {
#             "Score": 0.9887885451316833,
#             "Type": "PERSON",
#             "Text": "Benjamin Jameson",
#             "BeginOffset": 284,
#             "EndOffset": 300
#         },
#         {
#             "Score": 0.9309316277503967,
#             "Type": "QUANTITY",
#             "Text": "each",
#             "BeginOffset": 340,
#             "EndOffset": 344
#         },
#         {
#             "Score": 0.9898392558097839,
#             "Type": "LOCATION",
#             "Text": "123 Tenant St, San Diego, California 91932",
#             "BeginOffset": 477,
#             "EndOffset": 519
#         },
#         {
#             "Score": 0.9467597007751465,
#             "Type": "DATE",
#             "Text": "1st day of February\n, 2030",
#             "BeginOffset": 639,
#             "EndOffset": 665
#         },
#         {
#             "Score": 0.9719219207763672,
#             "Type": "DATE",
#             "Text": "1st day\nof February\n,\n2031",
#             "BeginOffset": 681,
#             "EndOffset": 707
#         },
#         {
#             "Score": 0.9985441565513611,
#             "Type": "QUANTITY",
#             "Text": "$1400",
#             "BeginOffset": 784,
#             "EndOffset": 789
#         },
#         {
#             "Score": 0.879361629486084,
#             "Type": "QUANTITY",
#             "Text": "1",
#             "BeginOffset": 829,
#             "EndOffset": 830
#         },
#         {
#             "Score": 0.6908817887306213,
#             "Type": "QUANTITY",
#             "Text": "every month",
#             "BeginOffset": 834,
#             "EndOffset": 845
#         },
#         {
#             "Score": 0.9978870153427124,
#             "Type": "QUANTITY",
#             "Text": "$1400",
#             "BeginOffset": 1008,
#             "EndOffset": 1013
#         },
#         {
#             "Score": 0.9605636596679688,
#             "Type": "QUANTITY",
#             "Text": "21 days",
#             "BeginOffset": 1164,
#             "EndOffset": 1171
#         },
#         {
#             "Score": 0.9809803366661072,
#             "Type": "PERSON",
#             "Text": "Jale Tond",
#             "BeginOffset": 1285,
#             "EndOffset": 1294
#         },
#         {
#             "Score": 0.9896635413169861,
#             "Type": "DATE",
#             "Text": "01/24/2030",
#             "BeginOffset": 1301,
#             "EndOffset": 1311
#         },
#         {
#             "Score": 0.9903541803359985,
#             "Type": "DATE",
#             "Text": "01/24/2030",
#             "BeginOffset": 1350,
#             "EndOffset": 1360
#         },
#         {
#             "Score": 0.9922319650650024,
#             "Type": "PERSON",
#             "Text": "Benjamin Jameson",
#             "BeginOffset": 1375,
#             "EndOffset": 1391
#         },
#         {
#             "Score": 0.715507447719574,
#             "Type": "QUANTITY",
#             "Text": "Page 1",
#             "BeginOffset": 1436,
#             "EndOffset": 1442
#         },
#         {
#             "Score": 0.5762502551078796,
#             "Type": "QUANTITY",
#             "Text": "1",
#             "BeginOffset": 1446,
#             "EndOffset": 1447
#         }
#     ],
#     "ResponseMetadata": {
#         "RequestId": "95a4bc57-1ad4-49c3-9024-48bcf18a2e96",
#         "HTTPStatusCode": 200,
#         "HTTPHeaders": {
#             "x-amzn-requestid": "95a4bc57-1ad4-49c3-9024-48bcf18a2e96",
#             "content-type": "application/x-amz-json-1.1",
#             "content-length": "2111",
#             "date": "Fri, 26 Nov 2021 16:01:11 GMT"
#         },
#         "RetryAttempts": 0
#     }
# }