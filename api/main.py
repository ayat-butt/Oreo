"""COCO Contracts API — FastAPI entrypoint.

Run locally:  uvicorn api.main:app --reload --port 8000  (from repo root)
Railway:      uvicorn api.main:app --host 0.0.0.0 --port $PORT

Phase 1 slice: /healthz + read-only /candidates against live Markaz.
SSO/JWT, /contracts (draft), and /email come in later phases (need the service token + app DB).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging

from api.settings import settings
from api.routers import candidates, contracts, email, email_candidates, access
from api.auth import sso

logger = logging.getLogger("coco.ingest")

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
app.include_router(email_candidates.router)
app.include_router(access.router)


# ── Background offer-email poller ────────────────────────────────────────────
# Watches the configured mailboxes for offer emails and ingests them as email_candidates.
# In-process APScheduler (Railway runs a single always-on instance). Guarded so it only
# starts when ingestion is enabled, mailbox tokens exist, and the app DB is configured.
_scheduler = None


def _run_ingest_safely() -> None:
    try:
        from api.services.email_ingest import ingest_offer_emails
        summary = ingest_offer_emails()
        logger.info("offer-email ingest: %s", summary)
    except Exception:  # noqa: BLE001 — never let a poll kill the scheduler thread
        logger.exception("offer-email ingest failed")


@app.on_event("startup")
def _ensure_tables() -> None:
    """Create any missing app-DB tables (idempotent; only adds, never alters).

    Keeps new tables like email_candidates in sync on deploy without a manual init step.
    Existing tables are untouched. No-op if the app DB isn't configured.
    """
    if not settings.APP_DATABASE_URL:
        return
    try:
        from api.db.base import Base, engine
        from api.db import models  # noqa: F401 — register all tables on Base.metadata
        Base.metadata.create_all(engine)
        logger.info("app DB tables ensured")
    except Exception:  # noqa: BLE001
        logger.exception("could not ensure app DB tables")


@app.on_event("startup")
def _seed_access_members() -> None:
    """Seed the access list from env (ALLOWLIST_EMAILS + OWNER_EMAILS) once, so the in-app
    User Management starts populated and owners are always admin. Idempotent."""
    if not settings.APP_DATABASE_URL:
        return
    try:
        from api.db.base import SessionLocal
        from api.db.models import AccessMember
        db = SessionLocal()
        try:
            existing = {m.email.lower(): m for m in db.query(AccessMember).all()}
            for email in sorted(settings.allowlist | settings.owner_emails):
                if email not in existing:
                    db.add(AccessMember(email=email, is_active=True,
                                        is_admin=email in settings.owner_emails, added_by="seed"))
            for email, m in existing.items():          # keep owners admin + active
                if email in settings.owner_emails and not (m.is_admin and m.is_active):
                    m.is_admin = True
                    m.is_active = True
            db.commit()
            logger.info("access members seeded")
        finally:
            db.close()
    except Exception:  # noqa: BLE001
        logger.exception("could not seed access members")


@app.on_event("startup")
def _start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    if not (settings.INGEST_ENABLED and settings.APP_DATABASE_URL and settings.inbox_tokens):
        logger.info("offer-email poller disabled (enabled=%s, app_db=%s, mailboxes=%d)",
                    settings.INGEST_ENABLED, bool(settings.APP_DATABASE_URL), len(settings.inbox_tokens))
        return
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        _scheduler = BackgroundScheduler(daemon=True)
        _scheduler.add_job(
            _run_ingest_safely,
            "interval",
            minutes=max(1, settings.INGEST_POLL_MINUTES),
            id="offer_email_ingest",
            next_run_time=None,           # first run scheduled one interval out; refresh endpoint is on-demand
            coalesce=True,
            max_instances=1,
        )
        _scheduler.start()
        logger.info("offer-email poller started: every %d min over %d mailbox(es)",
                    settings.INGEST_POLL_MINUTES, len(settings.inbox_tokens))
    except Exception:  # noqa: BLE001
        logger.exception("could not start offer-email poller")


@app.on_event("shutdown")
def _stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None


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

    # Offer-email ingestion readiness (non-secret: booleans, counts, mailbox addresses)
    health["checks"]["ingest"] = {
        "enabled": settings.INGEST_ENABLED,
        "anthropic_configured": bool(settings.ANTHROPIC_API_KEY),
        "offer_senders": settings.offer_senders,
        "mailboxes": sorted(settings.inbox_tokens.keys()),
        "since": settings.INGEST_SINCE or None,
        "lookback_days": settings.INGEST_LOOKBACK_DAYS,
    }
    return health


@app.get("/", tags=["meta"])
def root():
    return {"service": "COCO Contracts API", "docs": "/docs", "health": "/healthz"}
