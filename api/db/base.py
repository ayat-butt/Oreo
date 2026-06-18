"""App database (NEW Neon project) — SQLAlchemy engine + session.

This is the COCO app DB (drafts/audit/users/jobs). It is SEPARATE from the read-only
Markaz DB (which is accessed via hr_assistant/markaz_db.py with raw psycopg2).
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from api.settings import settings


class Base(DeclarativeBase):
    pass


# Engine is created only if APP_DATABASE_URL is configured (so /healthz works without it).
engine = (
    create_engine(settings.APP_DATABASE_URL, pool_pre_ping=True, future=True)
    if settings.APP_DATABASE_URL
    else None
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) if engine else None


def get_db():
    """FastAPI dependency — yields a session, always closes it."""
    if SessionLocal is None:
        raise RuntimeError("APP_DATABASE_URL is not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
