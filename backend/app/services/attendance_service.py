from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.schemas.attendance_schema import AttendanceCreate, AttendanceUpdate
from .audit_service import audit_service

class AttendanceService:
    def list_attendance(self, db: Session, course_id: str | None = None, student_id: str | None = None):
        query = db.query(Attendance)
        if course_id:
            query = query.filter(Attendance.course_id == course_id)
        if student_id:
            query = query.filter(Attendance.student_id == student_id)
        return query.order_by(Attendance.date.desc()).all()

    def create_attendance(self, db: Session, payload: AttendanceCreate, user_id=None) -> Attendance:
        item = Attendance(**payload.model_dump())
        db.add(item); db.commit(); db.refresh(item)
        audit_service.log(db, "attendance.create", "Attendance", str(item.id), user_id=user_id, after_data=payload.model_dump(mode="json"))
        return item

    def update_attendance(self, db: Session, attendance_id: str, payload: AttendanceUpdate, user_id=None) -> Attendance:
        item = db.get(Attendance, attendance_id)
        if not item:
            raise HTTPException(status_code=404, detail="Attendance not found")
        before = {"status": item.status.value, "remark": item.remark}
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit(); db.refresh(item)
        audit_service.log(db, "attendance.update", "Attendance", str(item.id), user_id=user_id, before_data=before, after_data=payload.model_dump(exclude_unset=True, mode="json"))
        return item

attendance_service = AttendanceService()
