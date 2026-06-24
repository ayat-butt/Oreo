"""Email-sourced candidates — offer details ingested from email (not Markaz).

Mirrors the Markaz candidates router so the frontend can reuse the form/card flow, but the
data comes from the app DB's email_candidates table (populated by the ingestion job).
Protected by SSO (current_user); only allowlisted P&C members can read.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db.base import get_db
from api.db.models import AppUser, EmailCandidate
from api.auth.deps import current_user
from api.schemas import (
    EmailCandidateOut, EmailCandidatesResponse, EmailCandidateDetail,
    EmpPrefill, IngestResult,
)
from api.services.audit import write_audit

router = APIRouter(prefix="/email-candidates", tags=["email-candidates"])

# Engine-required fields the offer email never carries → always manual in the review form.
_ALWAYS_MANUAL = ["entity", "employment_type", "gender", "hod_name", "hod_designation"]


def _to_card(row: EmailCandidate) -> EmailCandidateOut:
    return EmailCandidateOut(
        id=str(row.id),
        name=row.full_name,
        role=row.role,
        department=row.department,
        personal_email=row.personal_email,
        gross_salary=row.gross_salary,
        joining_date=row.joining_date,
        status=row.status,
        source_mailbox=row.source_mailbox,
        sender=row.sender,
        subject=row.subject,
        received_at=row.received_at,
        created_at=row.created_at,
    )


@router.get("", response_model=EmailCandidatesResponse)
def list_email_candidates(db: Session = Depends(get_db), user: AppUser = Depends(current_user)):
    """All ingested offer-email candidates, newest first; dismissed ones excluded."""
    rows = (
        db.query(EmailCandidate)
        .filter(EmailCandidate.status != "dismissed")
        .order_by(EmailCandidate.created_at.desc())
        .all()
    )
    cards = [_to_card(r) for r in rows]
    return EmailCandidatesResponse(
        total=len(cards),
        needs_review=sum(1 for r in rows if r.status == "new"),
        candidates=cards,
    )


@router.post("/refresh", response_model=IngestResult)
def refresh(user: AppUser = Depends(current_user)):
    """Run the offer-email ingestion now (manual trigger from the UI)."""
    from api.services.email_ingest import ingest_offer_emails
    summary = ingest_offer_emails()
    return IngestResult(**{k: summary.get(k) for k in IngestResult.model_fields if k in summary})


def _get(db: Session, candidate_id: str) -> EmailCandidate:
    try:
        cid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="email candidate not found")
    row = db.get(EmailCandidate, cid)
    if not row:
        raise HTTPException(status_code=404, detail="email candidate not found")
    return row


@router.get("/{candidate_id}", response_model=EmailCandidateDetail)
def email_candidate_detail(candidate_id: str, db: Session = Depends(get_db),
                           user: AppUser = Depends(current_user)):
    """Detail + engine-field prefill (tagged 'Email') + what still needs manual entry."""
    row = _get(db, candidate_id)
    prefill = EmpPrefill(
        name=row.full_name,
        cnic=row.cnic,
        email=row.personal_email,
        designation=row.role,
        department=row.department,
        salary=row.gross_salary,
        joining_date=row.joining_date,
        jd_text=row.jd_text,
    )
    missing: list[str] = []
    if not prefill.name: missing.append("name")
    if not prefill.cnic: missing.append("cnic")
    if not prefill.designation: missing.append("designation")
    if not prefill.department: missing.append("department")
    if not prefill.salary: missing.append("salary")
    if not prefill.joining_date: missing.append("joining_date")
    missing.extend(_ALWAYS_MANUAL)

    return EmailCandidateDetail(
        id=str(row.id),
        status=row.status,
        source_mailbox=row.source_mailbox,
        sender=row.sender,
        subject=row.subject,
        received_at=row.received_at,
        prefill=prefill,
        missing_fields=missing,
        hints={
            "source": "Auto-extracted from email — verify every field before drafting.",
            "received_at": row.received_at.isoformat() if row.received_at else None,
            "jd_text_available": "yes" if (row.jd_text or "").strip() else "no",
        },
    )


@router.post("/{candidate_id}/dismiss", response_model=EmailCandidateOut)
def dismiss(candidate_id: str, db: Session = Depends(get_db), user: AppUser = Depends(current_user)):
    """Hide a candidate that isn't a real hire (or was handled elsewhere)."""
    row = _get(db, candidate_id)
    row.status = "dismissed"
    db.commit()
    db.refresh(row)
    write_audit(db, user.email, "EMAIL_CANDIDATE_DISMISSED",
                detail={"id": str(row.id), "name": row.full_name})
    return _to_card(row)
