from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import create_access_token, verify_password
from app.models.user import User

class AuthService:
    def authenticate(self, db: Session, username: str, password: str) -> tuple[str, User]:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        token = create_access_token(str(user.id), {"role": user.role.value, "username": user.username})
        return token, user

auth_service = AuthService()
