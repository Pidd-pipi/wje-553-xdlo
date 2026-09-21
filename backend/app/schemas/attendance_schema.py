from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel
from app.core.enums import AttendanceStatus

class AttendanceBase(BaseModel):
    course_id: UUID
    student_id: UUID
    date: date
    status: AttendanceStatus = AttendanceStatus.PENDING
    remark: str | None = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: AttendanceStatus | None = None
    remark: str | None = None

class AttendanceRead(AttendanceBase):
    id: UUID
    student_name: str | None = None
    course_name: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
