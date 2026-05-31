## Scan routes

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Scan, Finding, ScanStatus
from app.scanner import run_scan
from app.schemas import ScanCreate, ScanRead, FindingRead

router = APIRouter()

@router.post("/scans", response_model=ScanRead, status_code=201)
def create_scan(payload: ScanCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    scan = Scan(
        aws_account_id=payload.aws_account_id,
        region=payload.region,
        status=ScanStatus.pending,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)    
    background_tasks.add_task(run_scan, scan.id)

    return scan

@router.get("/scans/{scan_id}/findings", response_model=list[FindingRead])
def get_scan_findings(scan_id: int, db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return db.query(Finding).filter(Finding.scan_id == scan_id).all()