from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.enums import CorrectionStatus
from app.schemas.attendance_schema import AttendanceCreate, AttendanceRead, AttendanceUpdate
from app.schemas.attendance_correction_schema import CorrectionApprove, CorrectionCreate, CorrectionRead, CorrectionReject
from app.services.attendance_service import attendance_service
from app.services.attendance_correction_service import attendance_correction_service

router = APIRouter(prefix="/attendance", tags=["attendance"])

def serialize(item):
    return AttendanceRead(
        id=str(item.id), course_id=str(item.course_id), student_id=str(item.student_id),
        course_name=item.course.name if item.course else None, student_name=item.student.name if item.student else None,
        date=item.date, status=item.status, remark=item.remark, created_at=item.created_at, updated_at=item.updated_at,
    )

def serialize_correction(item):
    attendance = item.attendance
    return CorrectionRead(
        id=str(item.id), attendance_id=str(item.attendance_id), student_id=str(item.student_id),
        requested_status=item.requested_status, reason=item.reason, status=item.status,
        reviewer_id=str(item.reviewer_id) if item.reviewer_id else None,
        review_comment=item.review_comment, reviewed_at=item.reviewed_at,
        created_at=item.created_at, updated_at=item.updated_at,
        student_name=item.student.name if item.student else None,
        course_name=attendance.course.name if attendance and attendance.course else None,
        attendance_date=attendance.date if attendance else None,
        current_status=attendance.status if attendance else None,
        reviewer_name=item.reviewer.full_name if item.reviewer else None,
    )

@router.get("", response_model=list[AttendanceRead])
def list_attendance(course_id: str | None = None, student_id: str | None = None, db: Session = Depends(get_db)):
    return [serialize(a) for a in attendance_service.list_attendance(db, course_id, student_id)]

@router.post("", response_model=AttendanceRead)
def create_attendance(payload: AttendanceCreate, request: Request, db: Session = Depends(get_db)):
    return serialize(attendance_service.create_attendance(db, payload, request.state.user["id"]))

@router.get("/corrections", response_model=list[CorrectionRead])
def list_corrections(request: Request, status: CorrectionStatus | None = None, db: Session = Depends(get_db)):
    return [serialize_correction(c) for c in attendance_correction_service.list_corrections(db, request.state.user, status.value if status else None)]

@router.post("/corrections", response_model=CorrectionRead, status_code=201)
def create_correction(payload: CorrectionCreate, request: Request, db: Session = Depends(get_db)):
    return serialize_correction(attendance_correction_service.create_correction(db, payload, request.state.user))

@router.post("/corrections/{correction_id}/approve", response_model=CorrectionRead)
def approve_correction(correction_id: str, request: Request, payload: CorrectionApprove | None = None, db: Session = Depends(get_db)):
    comment = payload.review_comment if payload else None
    return serialize_correction(attendance_correction_service.approve(db, correction_id, request.state.user, comment))

@router.post("/corrections/{correction_id}/reject", response_model=CorrectionRead)
def reject_correction(correction_id: str, payload: CorrectionReject, request: Request, db: Session = Depends(get_db)):
    return serialize_correction(attendance_correction_service.reject(db, correction_id, request.state.user, payload.review_comment))

@router.patch("/{attendance_id}", response_model=AttendanceRead)
def update_attendance(attendance_id: str, payload: AttendanceUpdate, request: Request, db: Session = Depends(get_db)):
    return serialize(attendance_service.update_attendance(db, attendance_id, payload, request.state.user["id"]))
