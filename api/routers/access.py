"""Access / user management — the app-managed sign-in allow list.

Admins (owners, or members flagged is_admin) can list/add/enable/disable/remove members.
Owner rows (settings.OWNER_EMAILS) are always allowed + admin and cannot be edited/removed.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.db.base import get_db
from api.db.models import AppUser, AccessMember
from api.auth.deps import current_admin
from api.schemas import AccessMemberOut, AccessListResponse, AccessMemberCreate, AccessMemberUpdate
from api.services.audit import write_audit
from api.settings import settings

router = APIRouter(prefix="/access", tags=["access"])


def _out(m: AccessMember) -> AccessMemberOut:
    is_owner = m.email.lower() in settings.owner_emails
    return AccessMemberOut(
        id=str(m.id), email=m.email, name=m.name,
        is_admin=m.is_admin or is_owner, is_active=m.is_active or is_owner,
        is_owner=is_owner, created_at=m.created_at,
    )


@router.get("/members", response_model=AccessListResponse)
def list_members(db: Session = Depends(get_db), admin: AppUser = Depends(current_admin)):
    rows = db.query(AccessMember).order_by(AccessMember.created_at).all()
    return AccessListResponse(members=[_out(m) for m in rows])


@router.post("/members", response_model=AccessMemberOut, status_code=201)
def add_member(body: AccessMemberCreate, db: Session = Depends(get_db),
               admin: AppUser = Depends(current_admin)):
    email = (body.email or "").strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    existing = db.query(AccessMember).filter(func.lower(AccessMember.email) == email).first()
    if existing:
        existing.is_active = True
        if body.name:
            existing.name = body.name.strip()
        db.commit()
        db.refresh(existing)
        write_audit(db, admin.email, "ACCESS_GRANTED", recipient=email, detail={"reactivated": True})
        return _out(existing)
    m = AccessMember(email=email, name=(body.name or "").strip() or None,
                     is_admin=False, is_active=True, added_by=admin.email)
    db.add(m)
    db.commit()
    db.refresh(m)
    write_audit(db, admin.email, "ACCESS_GRANTED", recipient=email)
    return _out(m)


def _get(db: Session, member_id: str) -> AccessMember:
    try:
        m = db.get(AccessMember, uuid.UUID(member_id))
    except ValueError:
        m = None
    if not m:
        raise HTTPException(status_code=404, detail="member not found")
    if m.email.lower() in settings.owner_emails:
        raise HTTPException(status_code=400, detail="Owner access can't be changed.")
    return m


@router.patch("/members/{member_id}", response_model=AccessMemberOut)
def update_member(member_id: str, body: AccessMemberUpdate, db: Session = Depends(get_db),
                  admin: AppUser = Depends(current_admin)):
    m = _get(db, member_id)
    if body.is_active is not None:
        m.is_active = body.is_active
    if body.is_admin is not None:
        m.is_admin = body.is_admin
    db.commit()
    db.refresh(m)
    write_audit(db, admin.email, "ACCESS_UPDATED", recipient=m.email,
                detail={"is_active": m.is_active, "is_admin": m.is_admin})
    return _out(m)


@router.delete("/members/{member_id}")
def remove_member(member_id: str, db: Session = Depends(get_db),
                  admin: AppUser = Depends(current_admin)):
    m = _get(db, member_id)
    email = m.email
    db.delete(m)
    db.commit()
    write_audit(db, admin.email, "ACCESS_REVOKED", recipient=email)
    return {"ok": True}
