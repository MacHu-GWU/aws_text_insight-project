# -*- coding: utf-8 -*-

import attr
import typing
from attrs_mate import AttrsClass


# --- SQS
@attr.s
class SQSRecord(AttrsClass):
    messageId: str = attr.ib()
    receiptHandle: str = attr.ib()
    body: str = attr.ib()
    attributes: dict = attr.ib()
    messageAttributes: dict = attr.ib()
    md5OfBody: str = attr.ib()
    eventSource: str = attr.ib()
    eventSourceARN: str = attr.ib()
    awsRegion: str = attr.ib()


@attr.s
class SQSEvent(AttrsClass):
    Records: typing.List[SQSRecord] = SQSRecord.ib_list_of_nested()


# --- S3Put
@attr.s
class Bucket(AttrsClass):
    name: str = attr.ib()
    ownerIdentity: dict = attr.ib()
    arn: str = attr.ib()


@attr.s
class Object(AttrsClass):
    key: str = attr.ib()
    size: int = attr.ib()
    eTag: str = attr.ib()
    sequencer: str = attr.ib()


@attr.s
class S3(AttrsClass):
    s3SchemaVersion: str = attr.ib()
    configurationId: str = attr.ib()
    bucket: Bucket = Bucket.ib_nested()
    object: Object = Object.ib_nested()


@attr.s
class S3PutRecord(AttrsClass):
    eventVersion: str = attr.ib()
    eventSource: str = attr.ib()
    awsRegion: str = attr.ib()
    eventTime: str = attr.ib()
    eventName: str = attr.ib()
    userIdentity: dict = attr.ib()
    requestParameters: dict = attr.ib()
    responseElements: dict = attr.ib()
    s3: S3 = S3.ib_nested()


@attr.s
class S3PutEvent(AttrsClass):
    Records: typing.List[S3PutRecord] = S3PutRecord.ib_list_of_nested()


# --- SNS

@attr.s
class SNS(AttrsClass):
    Type: str = attr.ib()
    MessageId: str = attr.ib()
    TopicArn: str = attr.ib()
    Subject: str = attr.ib()
    Message: str = attr.ib()
    Timestamp: str = attr.ib()
    SignatureVersion: str = attr.ib()
    Signature: str = attr.ib()
    SigningCertUrl: str = attr.ib()
    UnsubscribeUrl: str = attr.ib()
    MessageAttributes: dict = attr.ib()


@attr.s
class SNSRecord(AttrsClass):
    EventSource: str = attr.ib()
    EventVersion: str = attr.ib()
    EventSubscriptionArn: str = attr.ib()
    Sns: SNS = SNS.ib_nested()


@attr.s
class SNSEvent(AttrsClass):
    Records: typing.List[SNSRecord] = SNSRecord.ib_list_of_nested()
