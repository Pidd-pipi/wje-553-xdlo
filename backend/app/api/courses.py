from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.enums import CourseStatus
from app.schemas.common_schema import Message
from app.schemas.course_schema import CourseCreate, CourseRead, CourseUpdate
from app.services.course_service import course_service

router = APIRouter(prefix="/courses", tags=["courses"])

def serialize(course):
    return CourseRead(
        id=str(course.id), name=course.name, code=course.code, teacher_id=str(course.teacher_id),
        teacher_name=course.teacher.full_name if course.teacher else None,
        description=course.description, max_students=course.max_students, semester=course.semester,
        status=course.status, enrolled_count=len(course.enrollments), created_at=course.created_at, updated_at=course.updated_at,
    )

@router.get("", response_model=list[CourseRead])
def list_courses(keyword: str | None = None, status: CourseStatus | None = None, semester: str | None = None, db: Session = Depends(get_db)):
    return [serialize(c) for c in course_service.list_courses(db, keyword, status, semester)]

@router.post("", response_model=CourseRead)
def create_course(payload: CourseCreate, request: Request, db: Session = Depends(get_db)):
    return serialize(course_service.create_course(db, payload, request.state.user["id"]))

@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: str, db: Session = Depends(get_db)):
    return serialize(course_service.get_course(db, course_id))

@router.patch("/{course_id}", response_model=CourseRead)
def update_course(course_id: str, payload: CourseUpdate, request: Request, db: Session = Depends(get_db)):
    return serialize(course_service.update_course(db, course_id, payload, request.state.user["id"]))

@router.post("/{course_id}/enroll/{student_id}", response_model=Message)
def enroll(course_id: str, student_id: str, request: Request, db: Session = Depends(get_db)):
    course_service.enroll(db, course_id, student_id, request.state.user["id"])
    return {"message": "enrolled"}

@router.delete("/{course_id}/enroll/{student_id}", response_model=Message)
def drop(course_id: str, student_id: str, request: Request, db: Session = Depends(get_db)):
    course_service.drop(db, course_id, student_id, request.state.user["id"])
    return {"message": "dropped"}
