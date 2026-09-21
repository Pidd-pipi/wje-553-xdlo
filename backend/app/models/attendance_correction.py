import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.enums import CorrectionStatus
from .base import GUID, TimestampMixin

class AttendanceCorrection(TimestampMixin, Base):
    __tablename__ = "attendance_corrections"
    __table_args__ = (
        # DB 级硬约束：同一条考勤记录最多只能存在一条待审更正（兼容 SQLite / PostgreSQL）
        Index(
            "uq_correction_pending_attendance",
            "attendance_id",
            unique=True,
            sqlite_where=text("status = 'PENDING'"),
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    attendance_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("attendance.id", ondelete="CASCADE"), nullable=False)
    requester_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expected_status: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[CorrectionStatus] = mapped_column(Enum(CorrectionStatus), default=CorrectionStatus.PENDING, nullable=False)
    reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id"))
    review_remark: Mapped[Optional[str]] = mapped_column(String(500))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    attendance = relationship("Attendance", foreign_keys=[attendance_id])
    requester = relationship("User", foreign_keys=[requester_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
