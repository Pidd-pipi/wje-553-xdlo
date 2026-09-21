from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.enums import CorrectionStatus
from app.models.attendance import Attendance
from app.models.course import Course
from app.models.student import Student
from app.models.user import User
from app.schemas.correction_schema import CorrectionCreate, CorrectionRead, CorrectionRejectRequest, CorrectionReviewRequest
from app.services.correction_service import correction_service

router = APIRouter(prefix="/attendance/corrections", tags=["attendance-corrections"])

def serialize(db: Session, item) -> CorrectionRead:
    attendance = db.get(Attendance, item.attendance_id)
    requester = db.get(User, item.requester_id)
    reviewer = db.get(User, item.reviewer_id) if item.reviewer_id else None
    course = db.get(Course, attendance.course_id) if attendance else None
    student = db.get(Student, attendance.student_id) if attendance else None
    return CorrectionRead(
        id=item.id,
        attendance_id=item.attendance_id,
        requester_id=item.requester_id,
        requester_name=requester.full_name if requester else None,
        expected_status=item.expected_status,
        reason=item.reason,
        status=item.status,
        reviewer_id=item.reviewer_id,
        reviewer_name=reviewer.full_name if reviewer else None,
        review_remark=item.review_remark,
        reviewed_at=item.reviewed_at,
        course_id=attendance.course_id if attendance else None,
        course_name=course.name if course else None,
        student_id=attendance.student_id if attendance else None,
        student_name=student.name if student else None,
        attendance_date=attendance.date if attendance else None,
        current_status=attendance.status if attendance else None,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )

@router.get("", response_model=list[CorrectionRead])
def list_corrections(status: CorrectionStatus | None = None, request: Request = None, db: Session = Depends(get_db)):
    items = correction_service.list_corrections(db, request.state.user, status)
    return [serialize(db, c) for c in items]

@router.post("", response_model=CorrectionRead, status_code=201)
def create_correction(payload: CorrectionCreate, request: Request, db: Session = Depends(get_db)):
    item = correction_service.create_correction(db, payload, request.state.user)
    return serialize(db, item)

@router.post("/{correction_id}/approve", response_model=CorrectionRead)
def approve_correction(correction_id: str, payload: CorrectionReviewRequest, request: Request, db: Session = Depends(get_db)):
    item = correction_service.approve_correction(db, correction_id, payload.remark, request.state.user)
    return serialize(db, item)

@router.post("/{correction_id}/reject", response_model=CorrectionRead)
def reject_correction(correction_id: str, payload: CorrectionRejectRequest, request: Request, db: Session = Depends(get_db)):
    item = correction_service.reject_correction(db, correction_id, payload.reason, request.state.user)
    return serialize(db, item)
