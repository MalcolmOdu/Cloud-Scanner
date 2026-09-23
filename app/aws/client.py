## Credentials are deliberately not passed here: boto3 resolves them from its default
## credential chain (env vars, ~/.aws/credentials, IAM role, ...).

import boto3
from app.core.config import settings

def get_boto3_client(service: str):
    return boto3.client(service, region_name=settings.aws_region)
