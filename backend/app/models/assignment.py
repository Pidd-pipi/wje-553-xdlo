import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.enums import AssignmentStatus, AssignmentType
from .base import GUID, TimestampMixin

class Assignment(TimestampMixin, Base):
    __tablename__ = "assignments"

    course_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[AssignmentType] = mapped_column(Enum(AssignmentType), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_score: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))
    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus), default=AssignmentStatus.DRAFT, nullable=False)

    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
