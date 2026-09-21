from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.database import SessionLocal
from app.core.security import decode_token
from app.models.user import User

WHITE_LIST = ("/api/auth/login", "/api/health", "/docs", "/openapi.json", "/redoc")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or any(request.url.path.startswith(item) for item in WHITE_LIST):
            return await call_next(request)
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "", 1) if auth.startswith("Bearer ") else None
        if not token:
            return JSONResponse({"code": 401, "message": "Missing token", "detail": None}, status_code=401)
        payload = decode_token(token)
        if not payload:
            return JSONResponse({"code": 401, "message": "Invalid token", "detail": None}, status_code=401)
        db = SessionLocal()
        try:
            user = db.get(User, payload.get("sub"))
            if not user:
                return JSONResponse({"code": 401, "message": "User not found", "detail": None}, status_code=401)
            request.state.user = {"id": str(user.id), "username": user.username, "role": user.role.value, "full_name": user.full_name}
        finally:
            db.close()
        return await call_next(request)
