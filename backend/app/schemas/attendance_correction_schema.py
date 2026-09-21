from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.core.enums import AttendanceStatus, CorrectionStatus

class CorrectionCreate(BaseModel):
    attendance_id: UUID
    requested_status: AttendanceStatus
    reason: str = Field(min_length=1, max_length=500)

class CorrectionApprove(BaseModel):
    review_comment: str | None = Field(default=None, max_length=500)

class CorrectionReject(BaseModel):
    review_comment: str = Field(min_length=1, max_length=500)

class CorrectionRead(BaseModel):
    id: UUID
    attendance_id: UUID
    student_id: UUID
    requested_status: AttendanceStatus
    reason: str
    status: CorrectionStatus
    reviewer_id: UUID | None = None
    review_comment: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    student_name: str | None = None
    course_name: str | None = None
    attendance_date: date | None = None
    current_status: AttendanceStatus | None = None
    reviewer_name: str | None = None

    class Config:
        from_attributes = True
