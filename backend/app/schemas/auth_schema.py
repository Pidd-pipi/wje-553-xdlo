from uuid import UUID
from pydantic import BaseModel
from app.core.enums import UserRole

class LoginRequest(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: UUID
    username: str
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
