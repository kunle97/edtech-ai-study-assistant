import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.audit.models import AuditLog


def record_audit_event(
    db: Session,
    *,
    actor_id: uuid.UUID,
    action: str,
    target_type: str,
    target_id: str,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata_json=metadata or {},
    )

    db.add(audit_log)
    return audit_log