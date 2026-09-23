## Tests for the S3 Block Public Access check. AWS is mocked with moto, so no real account is touched.

import boto3
import pytest
from moto import mock_aws

from app.checks.s3 import PublicS3BucketCheck

REGION = "us-east-1"
BUCKET = "test-bucket"

ALL_BLOCKED = {
    "BlockPublicAcls": True,
    "IgnorePublicAcls": True,
    "BlockPublicPolicy": True,
    "RestrictPublicBuckets": True,
}


@pytest.fixture(autouse=True)
def fake_aws_credentials(monkeypatch):
    # Belt and braces: even if a call slipped past moto, it could never use real credentials.
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.delenv("AWS_PROFILE", raising=False)


def create_bucket(block_config=None):
    client = boto3.client("s3", region_name=REGION)
    client.create_bucket(Bucket=BUCKET)
    if block_config is not None:
        client.put_public_access_block(Bucket=BUCKET, PublicAccessBlockConfiguration=block_config)
    return client


def run_check(client):
    results = PublicS3BucketCheck().run(client)
    assert len(results) == 1
    return results[0]


@mock_aws
def test_bucket_without_block_public_access_is_flagged():
    result = run_check(create_bucket())

    assert result.passed is False
    assert result.resource_id == BUCKET


@mock_aws
def test_bucket_with_all_block_public_access_settings_is_safe():
    result = run_check(create_bucket(ALL_BLOCKED))

    assert result.passed is True


@mock_aws
def test_bucket_with_some_block_public_access_settings_is_flagged():
    result = run_check(create_bucket({**ALL_BLOCKED, "RestrictPublicBuckets": False}))

    assert result.passed is False
