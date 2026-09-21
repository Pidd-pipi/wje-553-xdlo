from datetime import date, datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.enums import AttendanceStatus, CorrectionStatus, UserRole
from app.models.attendance import Attendance
from app.models.attendance_correction import AttendanceCorrection
from app.models.course import Course
from app.models.student import Student
from app.models.user import User
from app.schemas.correction_schema import CorrectionCreate
from .audit_service import audit_service

CORRECTION_WINDOW_DAYS = 7

class CorrectionService:
    # ---------- helpers ----------
    def _get_student_profile(self, db: Session, user_id: str) -> Student:
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前账号未绑定学生档案")
        return student

    def _get_attendance_or_404(self, db: Session, attendance_id: str) -> Attendance:
        item = db.get(Attendance, attendance_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考勤记录不存在")
        return item

    def _get_correction_or_404(self, db: Session, correction_id: str) -> AttendanceCorrection:
        item = db.get(AttendanceCorrection, correction_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="更正申请不存在")
        return item

    def _require_reviewer(self, db: Session, user: dict, attendance: Attendance) -> None:
        """仅管理员或该考勤对应课程的任课教师可审批。"""
        role = user["role"]
        if role == UserRole.ADMIN.value:
            return
        if role != UserRole.TEACHER.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅任课教师或管理员可审批更正申请")
        course = db.get(Course, attendance.course_id)
        if not course or str(course.teacher_id) != user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能审批自己课程的考勤更正")

    # ---------- list ----------
    def list_corrections(self, db: Session, user: dict, status_filter: CorrectionStatus | None = None) -> list[AttendanceCorrection]:
        query = db.query(AttendanceCorrection).join(Attendance, AttendanceCorrection.attendance_id == Attendance.id)
        if user["role"] == UserRole.STUDENT.value:
            student = self._get_student_profile(db, user["id"])
            query = query.filter(Attendance.student_id == student.id)
        elif user["role"] == UserRole.TEACHER.value:
            query = query.join(Course, Attendance.course_id == Course.id).filter(Course.teacher_id == user["id"])
        if status_filter is not None:
            query = query.filter(AttendanceCorrection.status == status_filter)
        return query.order_by(AttendanceCorrection.created_at.desc()).all()

    # ---------- student submit ----------
    def create_correction(self, db: Session, payload: CorrectionCreate, user: dict) -> AttendanceCorrection:
        if user["role"] != UserRole.STUDENT.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅学生可提交考勤更正")

        student = self._get_student_profile(db, user["id"])
        attendance = self._get_attendance_or_404(db, str(payload.attendance_id))

        # 越权：只能为自己的考勤记录提交
        if str(attendance.student_id) != str(student.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能为自己的考勤记录提交更正")

        today = date.today()
        # 考勤后七天内
        if attendance.date > today:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="考勤尚未发生，无法更正")
        if (today - attendance.date).days > CORRECTION_WINDOW_DAYS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"仅可在考勤后 {CORRECTION_WINDOW_DAYS} 天内提交更正")

        # 应用层快速检查：已有待审申请整次拒绝
        existing = (
            db.query(AttendanceCorrection)
            .filter(
                AttendanceCorrection.attendance_id == attendance.id,
                AttendanceCorrection.status == CorrectionStatus.PENDING,
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该考勤记录已存在待审更正，请勿重复提交")

        if payload.expected_status == attendance.status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="期望状态与当前考勤状态一致，无需更正")

        item = AttendanceCorrection(
            attendance_id=attendance.id,
            requester_id=user["id"],
            expected_status=payload.expected_status.value,
            reason=payload.reason,
            status=CorrectionStatus.PENDING,
        )
        db.add(item)
        # DB 唯一部分索引兜底并发重复提交：只有一个事务能成功
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该考勤记录已存在待审更正，请勿重复提交")
        db.refresh(item)
        audit_service.log(
            db,
            "attendance_correction.create",
            "AttendanceCorrection",
            str(item.id),
            user_id=user["id"],
            after_data={
                "attendance_id": str(attendance.id),
                "expected_status": item.expected_status,
                "reason": item.reason,
                "status": item.status.value,
            },
        )
        return item

    # ---------- teacher/admin approve ----------
    def approve_correction(self, db: Session, correction_id: str, remark: str | None, user: dict) -> AttendanceCorrection:
        item = self._get_correction_or_404(db, correction_id)
        attendance = self._get_attendance_or_404(db, str(item.attendance_id))
        self._require_reviewer(db, user, attendance)

        # 条件更新：仅当仍为 PENDING 时才能抢占审批权，并发/重复处理只成功一次
        review_time = datetime.now(timezone.utc)
        corrected_remark = f"更正通过：{remark}" if remark else "考勤更正已通过"
        updated_rows = (
            db.query(AttendanceCorrection)
            .filter(
                AttendanceCorrection.id == item.id,
                AttendanceCorrection.status == CorrectionStatus.PENDING,
            )
            .update(
                {
                    AttendanceCorrection.status: CorrectionStatus.APPROVED,
                    AttendanceCorrection.reviewer_id: user["id"],
                    AttendanceCorrection.review_remark: remark,
                    AttendanceCorrection.reviewed_at: review_time,
                },
                synchronize_session=False,
            )
        )
        if updated_rows == 0:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该申请已处理，请勿重复审批")

        # 原子地更新考勤状态与备注；失败方不会改动考勤
        before = {"status": attendance.status.value, "remark": attendance.remark}
        attendance.status = AttendanceStatus(item.expected_status)
        attendance.remark = corrected_remark
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="审批失败，请重试")
        db.refresh(item)
        db.refresh(attendance)
        audit_service.log(
            db,
            "attendance_correction.approve",
            "AttendanceCorrection",
            str(item.id),
            user_id=user["id"],
            before_data=before,
            after_data={
                "attendance_id": str(attendance.id),
                "status": AttendanceStatus(item.expected_status).value,
                "remark": corrected_remark,
                "review_remark": remark,
            },
        )
        return item

    # ---------- teacher/admin reject ----------
    def reject_correction(self, db: Session, correction_id: str, reason: str, user: dict) -> AttendanceCorrection:
        item = self._get_correction_or_404(db, correction_id)
        attendance = self._get_attendance_or_404(db, str(item.attendance_id))
        self._require_reviewer(db, user, attendance)

        if not reason or not reason.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="驳回必须填写原因")

        review_time = datetime.now(timezone.utc)
        updated_rows = (
            db.query(AttendanceCorrection)
            .filter(
                AttendanceCorrection.id == item.id,
                AttendanceCorrection.status == CorrectionStatus.PENDING,
            )
            .update(
                {
                    AttendanceCorrection.status: CorrectionStatus.REJECTED,
                    AttendanceCorrection.reviewer_id: user["id"],
                    AttendanceCorrection.review_remark: reason.strip(),
                    AttendanceCorrection.reviewed_at: review_time,
                },
                synchronize_session=False,
            )
        )
        if updated_rows == 0:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该申请已处理，请勿重复审批")

        # 驳回不改考勤，只保留驳回原因
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="审批失败，请重试")
        db.refresh(item)
        audit_service.log(
            db,
            "attendance_correction.reject",
            "AttendanceCorrection",
            str(item.id),
            user_id=user["id"],
            after_data={
                "attendance_id": str(attendance.id),
                "status": CorrectionStatus.REJECTED.value,
                "reason": reason.strip(),
            },
        )
        return item

correction_service = CorrectionService()
