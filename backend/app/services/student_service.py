from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.student import Student
from app.schemas.student_schema import StudentCreate, StudentUpdate

class StudentService:
    def list_students(self, db: Session):
        return db.query(Student).order_by(Student.student_no).all()

    def get_student(self, db: Session, student_id: str) -> Student:
        student = db.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student

    def create_student(self, db: Session, payload: StudentCreate) -> Student:
        student = Student(**payload.model_dump())
        db.add(student); db.commit(); db.refresh(student)
        return student

    def update_student(self, db: Session, student_id: str, payload: StudentUpdate) -> Student:
        student = self.get_student(db, student_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(student, key, value)
        db.commit(); db.refresh(student)
        return student

student_service = StudentService()
