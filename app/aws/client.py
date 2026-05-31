import boto3
from app.core.config import settings

def get_boto3_client(service: str):
    return boto3.client(
        service,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key
    )