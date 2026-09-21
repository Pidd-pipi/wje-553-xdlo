from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth_schema import LoginRequest, TokenResponse, UserRead
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token, user = auth_service.authenticate(db, payload.username, payload.password)
    user_read = UserRead(
        id=user.id, username=user.username, full_name=user.full_name, role=user.role,
        student_id=user.student_profile.id if user.student_profile else None,
    )
    return {"access_token": token, "token_type": "bearer", "user": user_read}
