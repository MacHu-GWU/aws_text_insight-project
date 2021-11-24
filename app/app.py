# -*- coding: utf-8 -*-

import boto3
from pgr.lbd import hdl_hello_world
from chalice import Chalice

boto_ses = boto3.session.Session()
s3_client = boto_ses.client("s3")

app = Chalice(app_name="pgr")


@app.lambda_function(name="hello-world")
def handler_hello_world(event, context):
    return hdl_hello_world.handler(event, context)
