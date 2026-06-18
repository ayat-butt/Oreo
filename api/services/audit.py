"""Durable audit trail in the app DB (replaces the file-based oreo_audit.log for the web app)."""

from __future__ import annotations

import uuid
from sqlalchemy.orm import Session

from api.db.models import AuditEvent


def write_audit(
    db: Session,
    actor_email: str | None,
    action: str,
    request_id: uuid.UUID | None = None,
    recipient: str | None = None,
    detail: dict | None = None,
) -> AuditEvent:
    """Record one audit event. Actions: LOGIN, CONTRACT_DRAFTED, DRIVE_SHARED,
    EMAIL_DRAFTED, PILOT_SENT, LIVE_SENT, ..."""
    evt = AuditEvent(
        actor_email=actor_email,
        action=action,
        request_id=request_id,
        recipient=recipient,
        detail=detail,
    )
    db.add(evt)
    db.commit()
    return evt
