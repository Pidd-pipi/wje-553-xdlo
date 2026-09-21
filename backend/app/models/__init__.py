from app.core.database import Base
from .user import User
from .student import Student
from .course import Course, course_classes
from .enrollment import Enrollment
from .assignment import Assignment
from .submission import Submission
from .attendance import Attendance
from .audit_log import AuditLog

__all__ = ["Base", "User", "Student", "Course", "Enrollment", "Assignment", "Submission", "Attendance", "AuditLog"]
