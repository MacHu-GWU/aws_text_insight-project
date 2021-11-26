# -*- coding: utf-8 -*-

import boto3
import cottonformation as ctf
from aws_text_insight.config_init import config
from aws_text_insight.cf.per_stage_stack import create_template

tpl = create_template(config)

boto_ses = boto3.session.Session()
env = ctf.Env(boto_ses=boto_ses)
env.deploy(
    template=tpl,
    stack_name=config.env_name,
    bucket_name="aws-data-lab-sanhe-for-everything",
    include_iam=True,
)
