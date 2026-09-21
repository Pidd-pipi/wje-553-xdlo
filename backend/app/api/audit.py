from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/logs")
def list_logs(db: Session = Depends(get_db)):
    return audit_service.list_logs(db)
