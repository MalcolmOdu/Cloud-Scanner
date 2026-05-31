## Runs every check, takes the CheckResult objects they return, and translates the failures into Finding rows.

from app.db.session import SessionLocal
from app.db.models import Scan, Finding, ScanStatus
from app.checks.s3 import PublicS3BucketCheck
from app.aws.client import get_boto3_client

ALL_CHECKS = [PublicS3BucketCheck()]

def run_scan(scan_id: int) -> None:
    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        if scan is None:
            return
        scan.status = ScanStatus.running
        db.commit()

        client = get_boto3_client("s3")

        for check in ALL_CHECKS:
            results = check.run(client)
            for result in results:
                if not result.passed:
                    db.add(
                        Finding(
                            scan_id=scan.id,
                            check_id=result.check_id,
                            resource_id=result.resource_id,
                            severity=result.severity
                        )
                    )
        scan.status = ScanStatus.completed
        db.commit()

    except Exception as error:
        scan.status = ScanStatus.failed
        db.commit()
        raise
    finally:
        db.close()
