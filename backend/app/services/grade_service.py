from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.submission import Submission
from app.models.student import Student

class GradeService:
    def course_summary(self, db: Session, course_id: str | None = None):
        query = db.query(Submission).join(Submission.assignment)
        if course_id:
            query = query.filter_by(course_id=course_id)
        scores = [float(s.score or 0) for s in query.all()]
        if not scores:
            return {"average": 0, "highest": 0, "lowest": 0, "pass_rate": 0, "rows": []}
        return {
            "average": round(sum(scores) / len(scores), 1),
            "highest": max(scores),
            "lowest": min(scores),
            "pass_rate": round(len([s for s in scores if s >= 60]) / len(scores) * 100, 1),
            "rows": [],
        }

grade_service = GradeService()
