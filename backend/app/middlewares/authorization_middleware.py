from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.enums import UserRole

ADMIN_ONLY_PREFIXES = ("/api/audit",)
TEACHER_WRITE_PREFIXES = ("/api/assignments", "/api/attendance")

class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path.startswith(("/api/auth", "/api/health", "/docs", "/openapi", "/redoc")):
            return await call_next(request)
        user = getattr(request.state, "user", None)
        role = user.get("role") if user else None
        if any(request.url.path.startswith(p) for p in ADMIN_ONLY_PREFIXES) and role != UserRole.ADMIN.value:
            return JSONResponse({"code": 403, "message": "Permission denied", "detail": None}, status_code=403)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and any(request.url.path.startswith(p) for p in TEACHER_WRITE_PREFIXES):
            if role not in {UserRole.ADMIN.value, UserRole.TEACHER.value}:
                return JSONResponse({"code": 403, "message": "Permission denied", "detail": None}, status_code=403)
        return await call_next(request)
