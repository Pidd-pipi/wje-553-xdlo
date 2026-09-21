from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.core.enums import CourseStatus

class CourseBase(BaseModel):
    name: str
    code: str
    teacher_id: UUID
    description: str | None = None
    max_students: int = 60
    semester: str | None = None
    status: CourseStatus = CourseStatus.DRAFT

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    max_students: int | None = None
    semester: str | None = None
    status: CourseStatus | None = None

class CourseRead(CourseBase):
    id: UUID
    teacher_name: str | None = None
    enrolled_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
