from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.schemas.assignment_schema import AssignmentCreate, AssignmentUpdate
from .audit_service import audit_service

class AssignmentService:
    def list_assignments(self, db: Session, course_id: str | None = None):
        query = db.query(Assignment)
        if course_id:
            query = query.filter(Assignment.course_id == course_id)
        return query.order_by(Assignment.deadline.asc()).all()

    def get_assignment(self, db: Session, assignment_id: str) -> Assignment:
        item = db.get(Assignment, assignment_id)
        if not item:
            raise HTTPException(status_code=404, detail="Assignment not found")
        return item

    def create_assignment(self, db: Session, payload: AssignmentCreate, user_id=None) -> Assignment:
        item = Assignment(**payload.model_dump())
        db.add(item); db.commit(); db.refresh(item)
        audit_service.log(db, "assignment.create", "Assignment", str(item.id), user_id=user_id, after_data={"title": item.title})
        return item

    def update_assignment(self, db: Session, assignment_id: str, payload: AssignmentUpdate, user_id=None) -> Assignment:
        item = self.get_assignment(db, assignment_id)
        before = {"status": item.status.value, "title": item.title}
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit(); db.refresh(item)
        audit_service.log(db, "assignment.update", "Assignment", str(item.id), user_id=user_id, before_data=before, after_data=payload.model_dump(exclude_unset=True, mode="json"))
        return item

    def submit(self, db: Session, assignment_id: str, student_id: str, content: str):
        item = self.get_assignment(db, assignment_id)
        submission = db.query(Submission).filter_by(assignment_id=assignment_id, student_id=student_id).first()
        if submission:
            submission.content = content
        else:
            submission = Submission(assignment_id=item.id, student_id=student_id, content=content)
            db.add(submission)
        db.commit(); db.refresh(submission)
        return submission

assignment_service = AssignmentService()
