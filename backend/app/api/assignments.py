from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.assignment_schema import AssignmentCreate, AssignmentRead, AssignmentUpdate
from app.services.assignment_service import assignment_service

router = APIRouter(prefix="/assignments", tags=["assignments"])

class SubmissionPayload(BaseModel):
    student_id: str
    content: str

def serialize(item):
    return AssignmentRead(
        id=str(item.id), course_id=str(item.course_id), course_name=item.course.name if item.course else None,
        title=item.title, type=item.type, description=item.description, deadline=item.deadline,
        total_score=item.total_score, weight=item.weight, status=item.status,
        submissions_count=len(item.submissions), created_at=item.created_at, updated_at=item.updated_at,
    )

@router.get("", response_model=list[AssignmentRead])
def list_assignments(course_id: str | None = None, db: Session = Depends(get_db)):
    return [serialize(a) for a in assignment_service.list_assignments(db, course_id)]

@router.post("", response_model=AssignmentRead)
def create_assignment(payload: AssignmentCreate, request: Request, db: Session = Depends(get_db)):
    return serialize(assignment_service.create_assignment(db, payload, request.state.user["id"]))

@router.patch("/{assignment_id}", response_model=AssignmentRead)
def update_assignment(assignment_id: str, payload: AssignmentUpdate, request: Request, db: Session = Depends(get_db)):
    return serialize(assignment_service.update_assignment(db, assignment_id, payload, request.state.user["id"]))

@router.post("/{assignment_id}/submit")
def submit_assignment(assignment_id: str, payload: SubmissionPayload, db: Session = Depends(get_db)):
    item = assignment_service.submit(db, assignment_id, payload.student_id, payload.content)
    return {"id": str(item.id), "message": "submitted"}
