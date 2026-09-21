from datetime import date, datetime, timedelta, timezone
from app.core.database import Base, SessionLocal, engine
from app.core.enums import AssignmentStatus, AssignmentType, AttendanceStatus, CourseStatus, UserRole
from app.core.security import hash_password
from app.models.assignment import Assignment
from app.models.attendance import Attendance
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.user import User
from app import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if db.query(User).count():
        print('seed skipped')
    else:
        admin = User(username='admin', password_hash=hash_password('admin123'), full_name='系统管理员', role=UserRole.ADMIN)
        teacher = User(username='teacher', password_hash=hash_password('teacher123'), full_name='林老师', role=UserRole.TEACHER)
        stu_user = User(username='student', password_hash=hash_password('student123'), full_name='陈同学', role=UserRole.STUDENT)
        db.add_all([admin, teacher, stu_user]); db.flush()
        student = Student(student_no='S2026001', name='陈同学', grade='2026', class_name='计算机 1 班', email='student@example.edu', enroll_date=date.today(), user_id=stu_user.id)
        student2 = Student(student_no='S2026002', name='周同学', grade='2026', class_name='计算机 1 班', email='zhou@example.edu')
        course = Course(name='Python 数据分析实训', code='PY-DA-2026', teacher_id=teacher.id, description='面向校内培训项目的实践课程', max_students=60, semester='2026-Spring', status=CourseStatus.PUBLISHED)
        db.add_all([student, student2, course]); db.flush()
        db.add(Enrollment(course_id=course.id, student_id=student.id))
        assignment = Assignment(course_id=course.id, title='Pandas 清洗作业', type=AssignmentType.HOMEWORK, description='提交清洗报告和代码', deadline=datetime.now(timezone.utc)+timedelta(days=7), total_score=100, weight=0.2, status=AssignmentStatus.PUBLISHED)
        db.add(assignment)
        db.add(Attendance(course_id=course.id, student_id=student.id, date=date.today(), status=AttendanceStatus.PRESENT, remark='准时'))
        db.commit(); print('seed complete')
finally:
    db.close()
