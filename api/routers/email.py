"""Welcome-email endpoints: draft / pilot / live — each explicit and audited.

Guardrails:
  - draft : creates a Gmail draft (nothing sent)
  - pilot : SENDS to a test address (allowlist-checked) with a [TEST] subject prefix
  - live  : SENDS to the candidate; requires confirm=true AND ENVIRONMENT=production
CC is always allowlist-checked. Every send writes an EmailDispatch row + audit event.
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hr_assistant.config import get_google_services
from hr_assistant import email_service

from api.settings import settings
from api.db.base import get_db
from api.db.models import AppUser, ContractRequest, GeneratedDoc, EmailDispatch
from api.auth.deps import current_user
from api.schemas import EmailDraftRequest, EmailPilotRequest, EmailLiveRequest, EmailResult, EmailPreview
from api.services.audit import write_audit

router = APIRouter(prefix="/contracts", tags=["email"])


def _load(db: Session, request_id: uuid.UUID) -> tuple[ContractRequest, GeneratedDoc]:
    req = db.get(ContractRequest, request_id)
    if not req:
        raise HTTPException(404, "request not found")
    doc = (db.query(GeneratedDoc).filter(GeneratedDoc.request_id == req.id)
           .order_by(GeneratedDoc.created_at.desc()).first())
    if not doc or not doc.contract_id:
        raise HTTPException(409, "no generated contract for this request yet")
    return req, doc


def _record(db: Session, req: ContractRequest, user: AppUser, kind: str,
            to: str, cc: list[str] | None, subject: str, gmail_id: str, new_status: str) -> EmailResult:
    db.add(EmailDispatch(request_id=req.id, kind=kind, to_address=to, cc=cc,
                         subject=subject, gmail_id=gmail_id, sent_by=user.id))
    req.status = new_status
    db.commit()
    action = {"draft": "EMAIL_DRAFTED", "pilot": "PILOT_SENT", "live": "LIVE_SENT"}[kind]
    write_audit(db, user.email, action, request_id=req.id, recipient=to,
                detail={"subject": subject, "cc": cc or []})
    return EmailResult(kind=kind, to=to, subject=subject, gmail_id=gmail_id, request_status=req.status)


def _emp_with_form(emp: dict, form: str | None) -> tuple[dict, str, str]:
    """Return (emp merged with the chosen onboarding form, chosen_key, suggested_key)."""
    suggested = email_service.suggested_form_key(emp)
    key = (form or suggested).lower()
    if key not in email_service.ONBOARDING_FORMS:
        key = suggested
    return {**emp, "onboarding_form": email_service.form_url(key)}, key, suggested


@router.get("/{request_id}/email/preview", response_model=EmailPreview)
def email_preview(request_id: uuid.UUID, form: str | None = None, db: Session = Depends(get_db),
                  user: AppUser = Depends(current_user)):
    """Render the welcome-email subject + HTML body + attachment names (no send).
    `form` selects the data-collection form (orenda | niete); defaults to the role-based suggestion."""
    req, doc = _load(db, request_id)
    emp = req.emp_payload
    emp2, key, suggested = _emp_with_form(emp, form)
    from hr_assistant.email_service import _build_email_body
    attachments = [f"{emp['name']} - Contract.pdf"]
    if doc.nda_id:
        attachments.append(f"{emp['name']} - NDA.pdf")
    return EmailPreview(
        subject=f"Welcome to Taleemabad - {emp.get('designation', '')}",
        to=emp.get("email"),
        cc=emp.get("cc_list") or [],
        html_body=_build_email_body(emp2),
        attachments=attachments,
        form_key=key,
        form_suggested=suggested,
    )


@router.post("/{request_id}/email/draft", response_model=EmailResult)
def email_draft(request_id: uuid.UUID, body: EmailDraftRequest,
                db: Session = Depends(get_db), user: AppUser = Depends(current_user)):
    req, doc = _load(db, request_id)
    emp, _, _ = _emp_with_form(req.emp_payload, body.form)
    svcs = get_google_services(allow_interactive=False)
    res = email_service.draft_welcome_email(
        svcs["drive"], svcs["gmail"], emp, doc.contract_id, doc.nda_id, cc=body.cc)
    return _record(db, req, user, "draft", res["to"], body.cc, res["subject"], res["draft_id"], req.status)


@router.post("/{request_id}/email/pilot", response_model=EmailResult)
def email_pilot(request_id: uuid.UUID, body: EmailPilotRequest,
                db: Session = Depends(get_db), user: AppUser = Depends(current_user)):
    test_address = body.test_address or settings.TEST_PILOT_EMAIL
    if not test_address:
        raise HTTPException(400, "no test_address and TEST_PILOT_EMAIL not configured")
    req, doc = _load(db, request_id)
    emp, _, _ = _emp_with_form(req.emp_payload, body.form)
    svcs = get_google_services(allow_interactive=False)
    res = email_service.send_welcome_email(
        svcs["drive"], svcs["gmail"], emp, doc.contract_id, doc.nda_id,
        cc=body.cc, subject_prefix="[TEST] ", to_override=test_address)
    return _record(db, req, user, "pilot", res["to"], body.cc, res["subject"], res["message_id"], "pilot_sent")


@router.post("/{request_id}/email/live", response_model=EmailResult)
def email_live(request_id: uuid.UUID, body: EmailLiveRequest,
               db: Session = Depends(get_db), user: AppUser = Depends(current_user)):
    if not body.confirm:
        raise HTTPException(400, "live send requires confirm=true")
    if settings.ENVIRONMENT != "production":
        raise HTTPException(403, "live send is disabled outside production (ENVIRONMENT != production)")
    req, doc = _load(db, request_id)
    if not req.emp_payload.get("email"):
        raise HTTPException(400, "candidate email missing from emp payload")
    emp, _, _ = _emp_with_form(req.emp_payload, body.form)
    svcs = get_google_services(allow_interactive=False)
    res = email_service.send_welcome_email(
        svcs["drive"], svcs["gmail"], emp, doc.contract_id, doc.nda_id, cc=body.cc)
    return _record(db, req, user, "live", res["to"], body.cc, res["subject"], res["message_id"], "sent")
