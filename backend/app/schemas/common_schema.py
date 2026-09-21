from datetime import datetime
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int

class Message(BaseModel):
    message: str

class AuditLogRead(ORMBase):
    id: str
    user_id: str | None = None
    action: str
    target_type: str
    target_id: str | None = None
    before_data: dict | None = None
    after_data: dict | None = None
    ip_address: str | None = None
    created_at: datetime
