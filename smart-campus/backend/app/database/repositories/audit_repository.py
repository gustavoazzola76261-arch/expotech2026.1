from sqlalchemy.orm import Session

from app.database.models.audit_log_model import (
    AuditLogModel
)


class AuditRepository:

    @staticmethod
    def create(
        db: Session,
        data: dict
    ):
        audit_log = AuditLogModel(**data)

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    @staticmethod
    def get_all(
        db: Session
    ):
        return db.query(
            AuditLogModel
        ).all()

    @staticmethod
    def get_by_id(
        db: Session,
        audit_id: int
    ):
        return db.query(
            AuditLogModel
        ).filter(
            AuditLogModel.id == audit_id
        ).first()

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int
    ):
        return db.query(
            AuditLogModel
        ).filter(
            AuditLogModel.user_id == user_id
        ).all()

    @staticmethod
    def delete(
        db: Session,
        audit_id: int
    ):
        audit_log = db.query(
            AuditLogModel
        ).filter(
            AuditLogModel.id == audit_id
        ).first()

        if audit_log:
            db.delete(audit_log)
            db.commit()

        return audit_log