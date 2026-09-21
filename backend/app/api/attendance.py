from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.attendance_schema import AttendanceCreate, AttendanceRead, AttendanceUpdate
from app.services.attendance_service import attendance_service

router = APIRouter(prefix="/attendance", tags=["attendance"])

def serialize(item):
    return AttendanceRead(
        id=str(item.id), course_id=str(item.course_id), student_id=str(item.student_id),
        course_name=item.course.name if item.course else None, student_name=item.student.name if item.student else None,
        date=item.date, status=item.status, remark=item.remark, created_at=item.created_at, updated_at=item.updated_at,
    )

@router.get("", response_model=list[AttendanceRead])
def list_attendance(course_id: str | None = None, student_id: str | None = None, db: Session = Depends(get_db)):
    return [serialize(a) for a in attendance_service.list_attendance(db, course_id, student_id)]

@router.post("", response_model=AttendanceRead)
def create_attendance(payload: AttendanceCreate, request: Request, db: Session = Depends(get_db)):
    return serialize(attendance_service.create_attendance(db, payload, request.state.user["id"]))

@router.patch("/{attendance_id}", response_model=AttendanceRead)
def update_attendance(attendance_id: str, payload: AttendanceUpdate, request: Request, db: Session = Depends(get_db)):
    return serialize(attendance_service.update_attendance(db, attendance_id, payload, request.state.user["id"]))
