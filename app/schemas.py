## API request/response schemas

from datetime import datetime
from pydantic import BaseModel

class ScanCreate(BaseModel):
    aws_account_id: str
    region: str

class ScanRead(BaseModel):
    id: int
    aws_account_id: str
    region: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

class FindingRead(BaseModel):
    id: int
    scan_id: int
    check_id: str
    resource_id: str
    severity: str

    model_config = {"from_attributes": True}

