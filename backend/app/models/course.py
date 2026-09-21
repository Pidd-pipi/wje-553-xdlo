import uuid
from typing import Optional
from sqlalchemy import Enum, ForeignKey, Integer, String, Text, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.enums import CourseStatus
from .base import GUID, TimestampMixin

course_classes = Table(
    "course_classes",
    Base.metadata,
    Column("course_id", GUID(), ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    Column("class_name", String(50), primary_key=True),
)

class Course(TimestampMixin, Base):
    __tablename__ = "courses"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    teacher_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    max_students: Mapped[int] = mapped_column(Integer, default=60)
    semester: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[CourseStatus] = mapped_column(Enum(CourseStatus), default=CourseStatus.DRAFT, nullable=False)

    teacher = relationship("User", back_populates="taught_courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="course", cascade="all, delete-orphan")
