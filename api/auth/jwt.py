"""App session JWT (HS256) — minted after Google SSO, carried in an httpOnly cookie."""

from __future__ import annotations

import time
import jwt  # PyJWT

from api.settings import settings

_ALG = "HS256"


def mint_token(email: str, name: str | None) -> str:
    now = int(time.time())
    payload = {
        "sub": email.lower(),
        "name": name or "",
        "iat": now,
        "exp": now + settings.SESSION_TTL_HOURS * 3600,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=_ALG)


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[_ALG])
    except Exception:  # noqa: BLE001  (expired / invalid / tampered)
        return None
