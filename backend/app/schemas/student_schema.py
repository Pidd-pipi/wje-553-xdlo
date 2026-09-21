from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel

class StudentBase(BaseModel):
    student_no: str
    name: str
    grade: str | None = None
    class_name: str | None = None
    phone: str | None = None
    email: str | None = None
    enroll_date: date | None = None
    user_id: UUID | None = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: str | None = None
    grade: str | None = None
    class_name: str | None = None
    phone: str | None = None
    email: str | None = None

class StudentRead(StudentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
