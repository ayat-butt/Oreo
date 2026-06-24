"""App DB schema (Neon coco-app). Mirrors the approved plan.

Tables: app_users, contract_requests, generated_docs, email_dispatches, audit_events, jobs.
Markaz is never written here — this is the app's own state only.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="pnc", nullable=False)  # pnc | admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ContractRequest(Base):
    __tablename__ = "contract_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("app_users.id"))
    markaz_application_id: Mapped[int | None] = mapped_column(index=True)
    candidate_snapshot: Mapped[dict | None] = mapped_column(JSONB)   # what Markaz had at draft time
    emp_payload: Mapped[dict | None] = mapped_column(JSONB)          # the engine `emp` dict actually used
    entity: Mapped[str | None] = mapped_column(String(20))
    employment_type: Mapped[str | None] = mapped_column(String(20))
    # draft | generating | preview | pilot_sent | sent | failed
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    docs: Mapped[list["GeneratedDoc"]] = relationship(back_populates="request", cascade="all, delete-orphan")


class GeneratedDoc(Base):
    __tablename__ = "generated_docs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contract_requests.id", ondelete="CASCADE"))
    folder_id: Mapped[str | None] = mapped_column(String(100))
    folder_url: Mapped[str | None] = mapped_column(Text)
    contract_id: Mapped[str | None] = mapped_column(String(100))
    contract_url: Mapped[str | None] = mapped_column(Text)
    nda_id: Mapped[str | None] = mapped_column(String(100))
    nda_url: Mapped[str | None] = mapped_column(Text)
    shared_with: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request: Mapped["ContractRequest"] = relationship(back_populates="docs")


class EmailDispatch(Base):
    __tablename__ = "email_dispatches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contract_requests.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(10), nullable=False)  # draft | pilot | live
    to_address: Mapped[str | None] = mapped_column(String(320))
    cc: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    subject: Mapped[str | None] = mapped_column(Text)
    gmail_id: Mapped[str | None] = mapped_column(String(100))
    sent_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("app_users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    actor_email: Mapped[str | None] = mapped_column(String(320), index=True)
    # LOGIN | CONTRACT_DRAFTED | DRIVE_SHARED | EMAIL_DRAFTED | PILOT_SENT | LIVE_SENT
    action: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    recipient: Mapped[str | None] = mapped_column(String(320))
    detail: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class EmailCandidate(Base):
    """A candidate whose offer details arrived by email (from Aymen), not via Markaz.

    Populated by the background ingestion job (api/services/email_ingest.py). Starts as
    'new' (renders "Needs review"); Ayat verifies/corrects the auto-extracted fields in the
    contract form, then generating a draft flips it to 'drafted'. Dedup is on gmail_message_id.
    """
    __tablename__ = "email_candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    # Provenance
    source_mailbox: Mapped[str | None] = mapped_column(String(320))   # which inbox it arrived in
    gmail_message_id: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    gmail_thread_id: Mapped[str | None] = mapped_column(String(120))
    sender: Mapped[str | None] = mapped_column(String(320))
    subject: Mapped[str | None] = mapped_column(Text)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Auto-extracted offer fields (Claude) — all nullable; the form is the review gate
    full_name: Mapped[str | None] = mapped_column(String(200))
    cnic: Mapped[str | None] = mapped_column(String(40))
    personal_email: Mapped[str | None] = mapped_column(String(320))
    joining_date: Mapped[str | None] = mapped_column(String(40))   # ISO 'YYYY-MM-DD' when parseable
    gross_salary: Mapped[str | None] = mapped_column(String(40))
    role: Mapped[str | None] = mapped_column(String(200))
    department: Mapped[str | None] = mapped_column(String(200))
    jd_text: Mapped[str | None] = mapped_column(Text)
    raw_extract: Mapped[dict | None] = mapped_column(JSONB)         # full Claude JSON, for audit
    # State
    status: Mapped[str] = mapped_column(String(20), default="new", nullable=False)  # new | drafted | dismissed
    contract_request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)  # draft_contract
    request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    status: Mapped[str] = mapped_column(String(10), default="queued", nullable=False)  # queued|running|done|error
    result: Mapped[dict | None] = mapped_column(JSONB)
    error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
