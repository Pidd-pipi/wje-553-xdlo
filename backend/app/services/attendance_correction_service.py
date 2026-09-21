from datetime import date, datetime, timezone
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.enums import CorrectionStatus, UserRole
from app.models.attendance import Attendance
from app.models.attendance_correction import AttendanceCorrection
from app.models.course import Course
from app.models.student import Student
from app.schemas.attendance_correction_schema import CorrectionCreate
from .audit_service import audit_service

CORRECTION_WINDOW_DAYS = 7

class AttendanceCorrectionService:
    def list_corrections(self, db: Session, user: dict, status: str | None = None):
        query = db.query(AttendanceCorrection).join(Attendance, AttendanceCorrection.attendance_id == Attendance.id)
        if user["role"] == UserRole.STUDENT.value:
            student = self._current_student(db, user["id"])
            if not student:
                return []
            query = query.filter(AttendanceCorrection.student_id == student.id)
        elif user["role"] == UserRole.TEACHER.value:
            query = query.join(Course, Attendance.course_id == Course.id).filter(Course.teacher_id == UUID(str(user["id"])))
        if status:
            query = query.filter(AttendanceCorrection.status == CorrectionStatus(status))
        return query.order_by(AttendanceCorrection.created_at.desc()).all()

    def create_correction(self, db: Session, payload: CorrectionCreate, user: dict) -> AttendanceCorrection:
        if user["role"] != UserRole.STUDENT.value:
            raise HTTPException(status_code=403, detail="只有学生可以提交考勤更正申请")
        attendance = db.get(Attendance, payload.attendance_id)
        if not attendance:
            raise HTTPException(status_code=404, detail="Attendance not found")
        student = self._current_student(db, user["id"])
        if not student or attendance.student_id != student.id:
            raise HTTPException(status_code=403, detail="只能为自己的考勤记录提交更正")
        days = (date.today() - attendance.date).days
        if days < 0 or days > CORRECTION_WINDOW_DAYS:
            raise HTTPException(status_code=400, detail="考勤后七天内才能提交更正申请")
        pending = db.query(AttendanceCorrection).filter(
            AttendanceCorrection.attendance_id == attendance.id,
            AttendanceCorrection.status == CorrectionStatus.PENDING,
        ).first()
        if pending:
            raise HTTPException(status_code=409, detail="该考勤记录已有待审更正申请")
        item = AttendanceCorrection(
            attendance_id=attendance.id,
            student_id=student.id,
            requested_status=payload.requested_status,
            reason=payload.reason,
        )
        db.add(item)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="该考勤记录已有待审更正申请")
        audit_service.log(
            db, "attendance_correction.create", "AttendanceCorrection", str(item.id), user_id=user["id"],
            after_data={"attendance_id": str(attendance.id), "requested_status": payload.requested_status.value, "reason": payload.reason},
            commit=False,
        )
        db.commit()
        db.refresh(item)
        return item

    def approve(self, db: Session, correction_id: str, user: dict, review_comment: str | None = None) -> AttendanceCorrection:
        correction = self._get_for_review(db, correction_id, user)
        now = datetime.now(timezone.utc)
        result = db.execute(
            update(AttendanceCorrection)
            .where(AttendanceCorrection.id == correction.id, AttendanceCorrection.status == CorrectionStatus.PENDING)
            .values(status=CorrectionStatus.APPROVED, reviewer_id=UUID(str(user["id"])), review_comment=review_comment, reviewed_at=now)
        )
        if result.rowcount != 1:
            db.rollback()
            raise HTTPException(status_code=409, detail="该申请已被处理，请刷新查看")
        attendance = db.get(Attendance, correction.attendance_id)
        before = {"status": attendance.status.value, "remark": attendance.remark}
        attendance.status = correction.requested_status
        # attendance.remark 列为 String(200)，超出部分截断，完整原因保留在更正申请上
        attendance.remark = correction.reason[:200]
        audit_service.log(
            db, "attendance_correction.review", "AttendanceCorrection", str(correction.id), user_id=user["id"],
            before_data={"status": CorrectionStatus.PENDING.value},
            after_data={"status": CorrectionStatus.APPROVED.value, "review_comment": review_comment},
            commit=False,
        )
        audit_service.log(
            db, "attendance.update", "Attendance", str(attendance.id), user_id=user["id"],
            before_data=before,
            after_data={"status": attendance.status.value, "remark": attendance.remark},
            commit=False,
        )
        db.commit()
        db.refresh(correction)
        return correction

    def reject(self, db: Session, correction_id: str, user: dict, review_comment: str) -> AttendanceCorrection:
        if not review_comment or not review_comment.strip():
            raise HTTPException(status_code=400, detail="驳回必须填写原因")
        correction = self._get_for_review(db, correction_id, user)
        now = datetime.now(timezone.utc)
        result = db.execute(
            update(AttendanceCorrection)
            .where(AttendanceCorrection.id == correction.id, AttendanceCorrection.status == CorrectionStatus.PENDING)
            .values(status=CorrectionStatus.REJECTED, reviewer_id=UUID(str(user["id"])), review_comment=review_comment, reviewed_at=now)
        )
        if result.rowcount != 1:
            db.rollback()
            raise HTTPException(status_code=409, detail="该申请已被处理，请刷新查看")
        audit_service.log(
            db, "attendance_correction.review", "AttendanceCorrection", str(correction.id), user_id=user["id"],
            before_data={"status": CorrectionStatus.PENDING.value},
            after_data={"status": CorrectionStatus.REJECTED.value, "review_comment": review_comment},
            commit=False,
        )
        db.commit()
        db.refresh(correction)
        return correction

    def _get_for_review(self, db: Session, correction_id: str, user: dict) -> AttendanceCorrection:
        correction = db.get(AttendanceCorrection, correction_id)
        if not correction:
            raise HTTPException(status_code=404, detail="Correction not found")
        if user["role"] == UserRole.ADMIN.value:
            return correction
        if user["role"] == UserRole.TEACHER.value:
            course = db.get(Course, correction.attendance.course_id)
            if course and str(course.teacher_id) == str(user["id"]):
                return correction
        raise HTTPException(status_code=403, detail="只有任课教师或管理员可以审批更正申请")

    def _current_student(self, db: Session, user_id: str) -> Student | None:
        return db.query(Student).filter(Student.user_id == UUID(str(user_id))).first()

attendance_correction_service = AttendanceCorrectionService()
