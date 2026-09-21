from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.grade_service import grade_service

router = APIRouter(prefix="/grades", tags=["grades"])

@router.get("/summary")
def grade_summary(course_id: str | None = None, db: Session = Depends(get_db)):
    return grade_service.course_summary(db, course_id)
