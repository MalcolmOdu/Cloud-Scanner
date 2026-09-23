# Cloud Misconfiguration Scanner

A REST API that scans an AWS account for security misconfigurations and stores each one as a prioritized finding.

One request starts a scan. It runs in the background and records every misconfigured resource as a finding with a severity. You then fetch the findings, most severe first.

## Architecture

```
POST /scans ──► create Scan (pending) ──► return 201
                        │
                        └─► background task: run_scan(scan_id)
                                 │  status → running
                                 │  for each check in ALL_CHECKS:
                                 │      check.run(boto3 client) → [CheckResult, ...]
                                 │      failed results → Finding rows
                                 └─ status → completed / failed

GET /scans/{id}/findings ──► Findings for that scan, ordered critical → high → medium → low
```

- **Checks** (`app/checks/`) subclass `BaseCheck` and implement `run(client) -> list[CheckResult]`, returning one result per resource. They never touch the database, so each check can be tested alone with a mocked AWS client.
- **The scanner** (`app/scanner.py`) runs every registered check, saves failed results as `Finding` rows, and moves the scan through its status lifecycle.
- **The API** (`app/api/routes/`) creates scans and returns their findings, sorted by severity in the database query.

## Stack

**FastAPI** 
**SQLAlchemy + PostgreSQL** 
**Alembic** 
**boto3**
**Docker Compose**
**pytest + moto** 


## Running locally

**Prerequisites:** Python 3, Docker, and AWS credentials available to boto3 (e.g. `aws configure`, `aws sso login`, or `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` in your shell). They need `s3:ListAllMyBuckets` and `s3:GetBucketPublicAccessBlock`, both covered by AWS's managed `SecurityAudit` policy.

```bash
# 1. Install dependencies
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env             # DATABASE_URL and AWS_REGION

# 3. Start PostgreSQL
docker compose up -d

# 4. Create the schema
alembic upgrade head

# 5. Run the API
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`, with interactive docs at `/docs`.

> **Note:** AWS keys in `.env` are **not** used. `.env` only holds the app's own settings; supply credentials through your shell or an AWS profile.

### Example

Start a scan:

```bash
curl -X POST http://localhost:8000/scans \
  -H "Content-Type: application/json" \
  -d '{"aws_account_id": "123456789012", "region": "us-east-1"}'
```

```json
{"id": 1, "aws_account_id": "123456789012", "region": "us-east-1", "status": "pending", "created_at": "2026-09-22T10:00:00Z"}
```

The scan runs in the background, so give it a few seconds before fetching its findings:

```bash
curl http://localhost:8000/scans/1/findings
```

```json
[
  {"id": 1, "scan_id": 1, "check_id": "S3_001", "resource_id": "my-open-bucket", "severity": "high"}
]
```

Health check: `GET /health` → `{"status": "ok"}`

### Tests

```bash
pytest
```

No AWS credentials or network access needed.

## Current state

- **One check:** `S3_001`, S3 Block Public Access (severity `high`). A bucket is flagged unless all four Block Public Access settings are enabled.
- **Scan lifecycle:** `pending → running → completed / failed`, run as a background task.
- **Findings API:** a scan's findings, ordered by severity.
- **Unit tests:** three moto-based tests for the S3 check (no config, fully enabled, partially enabled).

**Scope of the S3 check:** it flags buckets without full Block Public Access. It does **not** determine that a bucket is actually public, which also depends on the bucket policy, ACLs, and account-level Block Public Access. Those aren't evaluated yet.

### Known limitations

- Scans run against whichever account the credentials belong to. `aws_account_id` is recorded but not verified.
- The client region comes from the `AWS_REGION` setting, not the scan request's `region`.
- No endpoint yet for a single scan's status; only its findings can be fetched.
- Background tasks run inside the API process, so an in-progress scan is lost on restart.
- If any check raises an error, the whole scan is marked `failed`.

## Roadmap

- **More checks:** e.g. IAM (root MFA, unused keys), EC2 security groups open to `0.0.0.0/0`, unencrypted EBS/RDS, CloudTrail disabled.
- **Per-check error handling:** record a failing check (e.g. `AccessDenied`) and continue the scan instead of failing it.
- **Wider test coverage:** API and scanner tests against a test database, plus tests for each new check.