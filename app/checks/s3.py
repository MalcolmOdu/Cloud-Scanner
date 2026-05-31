#Detects S3 buckets that are not fully protected by Block Public Access settings.

from botocore.exceptions import ClientError
from app.checks.base import BaseCheck, CheckResult

class PublicS3BucketCheck(BaseCheck):
    check_id = "S3_001"
    severity = "high"

    def run(self, client) -> list[CheckResult]:
        results: list[CheckResult] = []

        # List all S3 buckets in the account
        buckets = client.list_buckets().get("Buckets", [])
        for bucket in buckets:
            name = bucket["Name"]
            passed = self.is_fully_blocked(client, name)
            results.append(
                CheckResult(
                    check_id=self.check_id,
                    resource_id=name,
                    passed=passed,
                    severity=self.severity,
                    description=(
                        "Blocked Public Access is fully enabled." if passed else "Block Public Access is not fully enabled, buckets may be publicly available."
                    )
                )
            )
        return results

    def is_fully_blocked(self, client, bucket_name: str) -> bool:
        ## True if only all 4 Block Public Access settings are enabled.
        try:
            config = client.get_public_access_block(Bucket=bucket_name)
            block = config["PublicAccessBlockConfiguration"]
            return all([
                block["BlockPublicAcls"],
                block["IgnorePublicAcls"],
                block["BlockPublicPolicy"],
                block["RestrictPublicBuckets"]
            ])
        except ClientError as error:
            if error.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                return False
            raise
        