"""Current-user dependency.

Real Google SSO (JWT cookie) slots in here once the OAuth client exists. Until then, a
DEV stub identifies the user from an `X-Dev-User` header (or a default), so the rest of the
app can be built and tested. The stub is ONLY active when SSO is not configured AND
ENVIRONMENT != production — production with no SSO returns 401.
"""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.settings import settings
from api.db.base import get_db
from api.db.models import AppUser, AccessMember


def _allowed(email: str) -> bool:
    """Env/owner/domain check (no DB). DB-managed members are checked in is_email_allowed()."""
    email = email.lower()
    if email in settings.owner_emails:
        return True
    if settings.allowlist and email in settings.allowlist:
        return True
    return email.split("@")[-1] in settings.login_domains


def is_email_allowed(db: Session | None, email: str) -> bool:
    """May this email sign in? Owner / env allowlist / active access-list member / domain."""
    email = (email or "").lower()
    if _allowed(email):
        return True
    if db is not None:
        m = db.query(AccessMember).filter(
            func.lower(AccessMember.email) == email, AccessMember.is_active.is_(True)
        ).first()
        if m:
            return True
    return False


def is_admin_email(db: Session | None, email: str) -> bool:
    """May this email manage the access list? Owners, or active admin members."""
    email = (email or "").lower()
    if email in settings.owner_emails:
        return True
    if db is not None:
        return bool(db.query(AccessMember).filter(
            func.lower(AccessMember.email) == email,
            AccessMember.is_admin.is_(True), AccessMember.is_active.is_(True),
        ).first())
    return False


def _get_or_create_user(db: Session, email: str, name: str | None = None) -> AppUser:
    user = db.query(AppUser).filter(AppUser.email == email.lower()).one_or_none()
    if user is None:
        user = AppUser(email=email.lower(), name=name, role="pnc")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def current_user(
    request: Request,
    db: Session = Depends(get_db),
    x_dev_user: str | None = Header(default=None),
) -> AppUser:
    """Resolve the logged-in P&C member.

    If Google SSO is configured, require a valid app-session JWT cookie + allowlist.
    Otherwise (local dev only, non-production) fall back to the X-Dev-User stub.
    """
    if settings.GOOGLE_OAUTH_CLIENT_ID:
        from api.auth.jwt import verify_token
        token = request.cookies.get(settings.SESSION_COOKIE)
        payload = verify_token(token) if token else None
        if not payload:
            raise HTTPException(status_code=401, detail="not authenticated")
        email = (payload.get("sub") or "").lower()
        if not is_email_allowed(db, email):
            raise HTTPException(status_code=403, detail="not allowed")
        return _get_or_create_user(db, email, payload.get("name"))

    # Dev stub — only when SSO is not configured AND not production.
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=401, detail="SSO not configured")
    email = (x_dev_user or settings.TEST_PILOT_EMAIL or "dev@taleemabad.com").strip()
    return _get_or_create_user(db, email, name="Dev User")


def current_admin(user: AppUser = Depends(current_user), db: Session = Depends(get_db)) -> AppUser:
    """Require the caller to be an access-list admin (owner or active admin member)."""
    if not is_admin_email(db, user.email):
        raise HTTPException(status_code=403, detail="admins only")
    return user
