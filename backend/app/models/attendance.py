import uuid
from datetime import date
from typing import Optional
from sqlalchemy import Date, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.enums import AttendanceStatus
from .base import GUID, TimestampMixin

class Attendance(TimestampMixin, Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("course_id", "student_id", "date", name="uq_attendance_course_student_date"),)

    course_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), default=AttendanceStatus.PENDING, nullable=False)
    remark: Mapped[Optional[str]] = mapped_column(String(200))

    course = relationship("Course", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")
