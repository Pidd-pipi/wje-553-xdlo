from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.enums import CourseStatus
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.schemas.course_schema import CourseCreate, CourseUpdate
from .audit_service import audit_service

class CourseService:
    def list_courses(self, db: Session, keyword: str | None = None, status: CourseStatus | None = None, semester: str | None = None):
        query = db.query(Course)
        if keyword:
            query = query.filter(Course.name.ilike(f"%{keyword}%") | Course.code.ilike(f"%{keyword}%"))
        if status:
            query = query.filter(Course.status == status)
        if semester:
            query = query.filter(Course.semester == semester)
        return query.order_by(Course.created_at.desc()).all()

    def get_course(self, db: Session, course_id: str) -> Course:
        course = db.get(Course, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course

    def create_course(self, db: Session, payload: CourseCreate, user_id=None) -> Course:
        course = Course(**payload.model_dump())
        db.add(course)
        db.commit(); db.refresh(course)
        audit_service.log(db, "course.create", "Course", str(course.id), user_id=user_id, after_data={"code": course.code, "status": course.status.value})
        return course

    def update_course(self, db: Session, course_id: str, payload: CourseUpdate, user_id=None) -> Course:
        course = self.get_course(db, course_id)
        before = {"status": course.status.value, "name": course.name}
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(course, key, value)
        db.commit(); db.refresh(course)
        audit_service.log(db, "course.update", "Course", str(course.id), user_id=user_id, before_data=before, after_data=payload.model_dump(exclude_unset=True, mode="json"))
        return course

    def enroll(self, db: Session, course_id: str, student_id: str, user_id=None) -> Enrollment:
        course = self.get_course(db, course_id)
        if len(course.enrollments) >= course.max_students:
            raise HTTPException(status_code=400, detail="Course is full")
        if db.query(Enrollment).filter_by(course_id=course_id, student_id=student_id).first():
            raise HTTPException(status_code=400, detail="Already enrolled")
        if not db.get(Student, student_id):
            raise HTTPException(status_code=404, detail="Student not found")
        item = Enrollment(course_id=course_id, student_id=student_id)
        db.add(item); db.commit(); db.refresh(item)
        audit_service.log(db, "enrollment.create", "Course", course_id, user_id=user_id, after_data={"student_id": student_id})
        return item

    def drop(self, db: Session, course_id: str, student_id: str, user_id=None) -> None:
        item = db.query(Enrollment).filter_by(course_id=course_id, student_id=student_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        db.delete(item); db.commit()
        audit_service.log(db, "enrollment.delete", "Course", course_id, user_id=user_id, before_data={"student_id": student_id})

course_service = CourseService()
