from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.enums import UserRole

ADMIN_ONLY_PREFIXES = ("/api/audit",)
TEACHER_WRITE_PREFIXES = ("/api/assignments", "/api/attendance")
# 学生可访问的考勤相关路径：提交更正申请（审批动作仍仅教师/管理员）
STUDENT_ATTENDANCE_ALLOWED_POST = "/api/attendance/corrections"

class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path.startswith(("/api/auth", "/api/health", "/docs", "/openapi", "/redoc")):
            return await call_next(request)
        user = getattr(request.state, "user", None)
        role = user.get("role") if user else None
        if any(request.url.path.startswith(p) for p in ADMIN_ONLY_PREFIXES) and role != UserRole.ADMIN.value:
            return JSONResponse({"code": 403, "message": "Permission denied", "detail": None}, status_code=403)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and any(request.url.path.startswith(p) for p in TEACHER_WRITE_PREFIXES):
            # 学生仅可对考勤更正发起申请，审批（/approve、/reject）在 Service 层强制教师/管理员
            student_submit = request.method == "POST" and request.url.path == STUDENT_ATTENDANCE_ALLOWED_POST and role == UserRole.STUDENT.value
            if not student_submit and role not in {UserRole.ADMIN.value, UserRole.TEACHER.value}:
                return JSONResponse({"code": 403, "message": "Permission denied", "detail": None}, status_code=403)
        return await call_next(request)
