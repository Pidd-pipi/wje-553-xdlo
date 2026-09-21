from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.core.enums import AttendanceStatus, CorrectionStatus

class CorrectionCreate(BaseModel):
    attendance_id: UUID
    expected_status: AttendanceStatus
    reason: str | None = Field(default=None, max_length=500)

class CorrectionReviewRequest(BaseModel):
    remark: str | None = Field(default=None, max_length=500)

class CorrectionRejectRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)

class CorrectionRead(BaseModel):
    id: UUID
    attendance_id: UUID
    requester_id: UUID
    requester_name: str | None = None
    expected_status: AttendanceStatus
    reason: str | None = None
    status: CorrectionStatus
    reviewer_id: UUID | None = None
    reviewer_name: str | None = None
    review_remark: str | None = None
    reviewed_at: datetime | None = None
    course_id: UUID | None = None
    course_name: str | None = None
    student_id: UUID | None = None
    student_name: str | None = None
    attendance_date: datetime | None = None
    current_status: AttendanceStatus | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
