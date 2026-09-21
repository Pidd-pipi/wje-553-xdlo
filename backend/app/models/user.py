import uuid
from typing import Optional
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.enums import UserRole
from .base import GUID, TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    student_profile = relationship("Student", back_populates="user", uselist=False)
    taught_courses = relationship("Course", back_populates="teacher")
