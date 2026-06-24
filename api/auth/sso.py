"""Google Workspace SSO — Authorization Code flow, server-side, issuing an app JWT cookie.

/auth/login    → redirect to Google consent
/auth/callback → verify Google ID token, allowlist-check, set session cookie, redirect to frontend
/auth/me       → current user (from cookie)
/auth/logout   → clear cookie
"""

from __future__ import annotations

import secrets
import urllib.parse
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session

from api.settings import settings
from api.db.base import get_db
from api.auth.jwt import mint_token, verify_token
from api.auth.deps import _allowed, _get_or_create_user
from api.services.audit import write_audit

router = APIRouter(prefix="/auth", tags=["auth"])

_GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
_STATE_COOKIE = "coco_oauth_state"


def _cookie_kwargs() -> dict:
    prod = settings.ENVIRONMENT == "production"
    # cross-site cookie (Vercel ↔ Railway) requires SameSite=None + Secure in prod
    return {"httponly": True, "secure": prod, "samesite": "none" if prod else "lax", "path": "/"}


@router.get("/login")
def login():
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise HTTPException(503, "SSO not configured")
    state = secrets.token_urlsafe(24)
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    if settings.login_domains:
        params["hd"] = sorted(settings.login_domains)[0]  # UI hint only; allowlist is the real gate
    resp = RedirectResponse(_GOOGLE_AUTH + "?" + urllib.parse.urlencode(params))
    resp.set_cookie(_STATE_COOKIE, state, max_age=600, **_cookie_kwargs())
    return resp


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db),
                   code: str = "", state: str = ""):
    if not code or not state or state != request.cookies.get(_STATE_COOKIE):
        raise HTTPException(400, "invalid OAuth state")
    async with httpx.AsyncClient(timeout=20) as client:
        tok = await client.post(_GOOGLE_TOKEN, data={
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.OAUTH_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
    if tok.status_code != 200:
        raise HTTPException(400, f"token exchange failed ({tok.status_code}): {tok.text[:300]}")
    id_tok = tok.json().get("id_token")
    info = google_id_token.verify_oauth2_token(
        id_tok, google_requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID
    )
    email = (info.get("email") or "").lower()
    if not info.get("email_verified") or not _allowed(email):
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=not_allowed")

    user = _get_or_create_user(db, email, info.get("name"))
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    write_audit(db, email, "LOGIN")

    resp = RedirectResponse(f"{settings.FRONTEND_URL}/dashboard")
    resp.set_cookie(settings.SESSION_COOKIE, mint_token(email, info.get("name")),
                    max_age=settings.SESSION_TTL_HOURS * 3600, **_cookie_kwargs())
    resp.delete_cookie(_STATE_COOKIE, path="/")
    return resp


@router.get("/me")
def me(request: Request):
    token = request.cookies.get(settings.SESSION_COOKIE)
    payload = verify_token(token) if token else None
    if not payload:
        raise HTTPException(401, "not authenticated")
    return {"email": payload.get("sub"), "name": payload.get("name")}


@router.post("/logout")
def logout():
    resp = RedirectResponse(f"{settings.FRONTEND_URL}/login", status_code=303)
    resp.delete_cookie(settings.SESSION_COOKIE, path="/")
    return resp
