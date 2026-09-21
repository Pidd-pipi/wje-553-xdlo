from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

class AuditService:
    def list_logs(self, db: Session, limit: int = 100):
        return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()

    def log(self, db: Session, action: str, target_type: str, target_id: str | None = None, user_id=None, before_data=None, after_data=None, ip_address=None):
        item = AuditLog(user_id=user_id, action=action, target_type=target_type, target_id=target_id, before_data=before_data, after_data=after_data, ip_address=ip_address)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

audit_service = AuditService()
