import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.enums import AttendanceStatus, CorrectionStatus
from .base import GUID, TimestampMixin

class AttendanceCorrection(TimestampMixin, Base):
    __tablename__ = "attendance_corrections"
    __table_args__ = (
        Index(
            "uq_attendance_corrections_pending",
            "attendance_id",
            unique=True,
            sqlite_where=text("status = 'PENDING'"),
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    attendance_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("attendance.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    requested_status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[CorrectionStatus] = mapped_column(Enum(CorrectionStatus), default=CorrectionStatus.PENDING, nullable=False)
    reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id"))
    review_comment: Mapped[Optional[str]] = mapped_column(String(500))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    attendance = relationship("Attendance")
    student = relationship("Student")
    reviewer = relationship("User")
