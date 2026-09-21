from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.student_schema import StudentCreate, StudentRead, StudentUpdate
from app.services.student_service import student_service

router = APIRouter(prefix="/students", tags=["students"])

@router.get("", response_model=list[StudentRead])
def list_students(db: Session = Depends(get_db)):
    return student_service.list_students(db)

@router.post("", response_model=StudentRead)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    return student_service.create_student(db, payload)

@router.patch("/{student_id}", response_model=StudentRead)
def update_student(student_id: str, payload: StudentUpdate, db: Session = Depends(get_db)):
    return student_service.update_student(db, student_id, payload)
