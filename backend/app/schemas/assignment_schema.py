from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel
from app.core.enums import AssignmentStatus, AssignmentType

class AssignmentBase(BaseModel):
    course_id: UUID
    title: str
    type: AssignmentType
    description: str | None = None
    deadline: datetime
    total_score: Decimal
    weight: Decimal | None = None
    status: AssignmentStatus = AssignmentStatus.DRAFT

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    total_score: Decimal | None = None
    weight: Decimal | None = None
    status: AssignmentStatus | None = None

class AssignmentRead(AssignmentBase):
    id: UUID
    course_name: str | None = None
    submissions_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
