import enum
from datetime import datetime, timezone

from sqlalchemy import Enum, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class ScanStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    aws_account_id: Mapped[str] = mapped_column(String(20))
    region: Mapped[str] = mapped_column(String(30))

    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus, native_enum=False),
        default = ScanStatus.pending
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        default = lambda: datetime.now(timezone.utc)
    )

    findings: Mapped[list["Finding"]] = relationship(back_populates="scan")


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"))

    check_id: Mapped[str] = mapped_column(String(20))
    resource_id: Mapped[str] = mapped_column(String(200))

    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, native_enum=False)
    )

    scan: Mapped[Scan] = relationship(back_populates="findings")