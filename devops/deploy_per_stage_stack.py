# -*- coding: utf-8 -*-

import boto3
import cottonformation as cf
from aws_text_insight.config_init import config
from aws_text_insight.cf.per_stage_stack import PerStageStack

stack = PerStageStack(config=config)

tpl = cf.Template(Description="Demo: Resource Group best practice")

tpl.add(stack.rg1_s3_buckets)
tpl.add(stack.rg2_iam_roles)
tpl.add(stack.rg3_sns_topic)

tpl.batch_tagging(
    overwrite=True,
    ProjectName=config.project_name_slugify,
    EnvName=config.env_name,
)

boto_ses = boto3.session.Session()
env = cf.Env(boto_ses=boto_ses)
env.deploy(
    template=tpl,
    stack_name=config.cf_stack_name,
    bucket_name="aws-data-lab-sanhe-for-everything",
    include_iam=True,
)
