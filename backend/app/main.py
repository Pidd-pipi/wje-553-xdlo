from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import assignments, attendance, audit, auth, courses, grades, students
from app.core.config import get_settings
from app.core.database import Base, engine
from app.middlewares.auth_middleware import AuthMiddleware
from app.middlewares.authorization_middleware import AuthorizationMiddleware
from app.middlewares.audit_middleware import AuditMiddleware
from app.middlewares.error_handler import register_error_handlers
from app import models

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(AuditMiddleware)
app.add_middleware(AuthorizationMiddleware)
app.add_middleware(AuthMiddleware)
register_error_handlers(app)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CampusHub"}

for router in [auth.router, courses.router, students.router, assignments.router, attendance.router, grades.router, audit.router]:
    app.include_router(router, prefix=settings.api_prefix)
