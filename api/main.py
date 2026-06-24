"""COCO Contracts API — FastAPI entrypoint.

Run locally:  uvicorn api.main:app --reload --port 8000  (from repo root)
Railway:      uvicorn api.main:app --host 0.0.0.0 --port $PORT

Phase 1 slice: /healthz + read-only /candidates against live Markaz.
SSO/JWT, /contracts (draft), and /email come in later phases (need the service token + app DB).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.settings import settings
from api.routers import candidates, contracts, email
from api.auth import sso

app = FastAPI(title="COCO Contracts API", version="0.1.0")

# Allowed browser origins: the configured list + FRONTEND_URL (trailing slashes stripped),
# plus a regex covering this project's Vercel deployments (production + preview/branch URLs).
_allowed_origins = {o.rstrip("/") for o in settings.cors_origins}
_allowed_origins.add(settings.FRONTEND_URL.rstrip("/"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(_allowed_origins),
    allow_origin_regex=r"https://oreo[-a-z0-9]*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sso.router)
app.include_router(candidates.router)
app.include_router(contracts.router)
app.include_router(email.router)


@app.get("/healthz", tags=["meta"])
def healthz():
    """Liveness + dependency check. Reports which integrations are configured/reachable."""
    health = {"status": "ok", "environment": settings.ENVIRONMENT, "checks": {}}

    # Markaz reachable? (read-only)
    try:
        from hr_assistant import markaz_db
        with markaz_db._conn() as (cur, _):
            cur.execute("SELECT 1")
            cur.fetchone()
        health["checks"]["markaz_db"] = "ok"
    except Exception as e:  # noqa: BLE001
        health["checks"]["markaz_db"] = f"error: {type(e).__name__}"
        health["status"] = "degraded"

    # App DB reachable? (read/write Neon)
    if settings.APP_DATABASE_URL:
        try:
            from api.db.base import engine
            from sqlalchemy import text
            with engine.connect() as c:
                c.execute(text("SELECT 1"))
            health["checks"]["app_db"] = "ok"
        except Exception as e:  # noqa: BLE001
            health["checks"]["app_db"] = f"error: {type(e).__name__}"
            health["status"] = "degraded"
    else:
        health["checks"]["app_db"] = "not configured"

    # Configuration presence (not values)
    health["checks"]["app_db_configured"] = bool(settings.APP_DATABASE_URL)
    health["checks"]["google_service_token_configured"] = bool(settings.GOOGLE_SERVICE_TOKEN_JSON)
    health["checks"]["sso_configured"] = bool(settings.GOOGLE_OAUTH_CLIENT_ID)
    health["checks"]["allowlist_count"] = len(settings.allowlist)
    return health


@app.get("/", tags=["meta"])
def root():
    return {"service": "COCO Contracts API", "docs": "/docs", "health": "/healthz"}
