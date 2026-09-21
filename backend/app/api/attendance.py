from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.enums import UserRole
from app.models.attendance_correction import AttendanceCorrection
from app.models.student import Student
from app.schemas.attendance_schema import AttendanceCreate, AttendanceRead, AttendanceUpdate
from app.services.attendance_service import attendance_service

router = APIRouter(prefix="/attendance", tags=["attendance"])

def _latest_corrections_map(db: Session, items: list) -> dict:
    if not items:
        return {}
    ids = [a.id for a in items]
    rows = (
        db.query(AttendanceCorrection)
        .filter(AttendanceCorrection.attendance_id.in_(ids))
        .order_by(AttendanceCorrection.created_at.desc())
        .all()
    )
    latest: dict = {}
    for row in rows:
        latest.setdefault(str(row.attendance_id), row)
    return latest

def serialize(item, latest: AttendanceCorrection | None = None) -> AttendanceRead:
    return AttendanceRead(
        id=str(item.id), course_id=str(item.course_id), student_id=str(item.student_id),
        course_name=item.course.name if item.course else None, student_name=item.student.name if item.student else None,
        date=item.date, status=item.status, remark=item.remark,
        correction_status=latest.status if latest else None,
        correction_id=str(latest.id) if latest else None,
        created_at=item.created_at, updated_at=item.updated_at,
    )

@router.get("", response_model=list[AttendanceRead])
def list_attendance(request: Request, course_id: str | None = None, student_id: str | None = None, db: Session = Depends(get_db)):
    user = request.state.user
    # 学生只能查看自己的考勤（忽略其伪造的 student_id）
    if user["role"] == UserRole.STUDENT.value:
        profile = db.query(Student).filter(Student.user_id == user["id"]).first()
        if not profile:
            return []
        student_id = str(profile.id)
    items = attendance_service.list_attendance(db, course_id, student_id)
    latest_map = _latest_corrections_map(db, items)
    return [serialize(a, latest_map.get(str(a.id))) for a in items]

@router.post("", response_model=AttendanceRead)
def create_attendance(payload: AttendanceCreate, request: Request, db: Session = Depends(get_db)):
    return serialize(attendance_service.create_attendance(db, payload, request.state.user["id"]))

@router.patch("/{attendance_id}", response_model=AttendanceRead)
def update_attendance(attendance_id: str, payload: AttendanceUpdate, request: Request, db: Session = Depends(get_db)):
    return serialize(attendance_service.update_attendance(db, attendance_id, payload, request.state.user["id"]))
