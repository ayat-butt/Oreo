"""Ingest offer-letter emails into the app DB as email_candidates.

For each configured mailbox, search for recent mail from the offer sender, parse any
message we haven't seen, ask Claude to extract the hire details, and upsert a 'new'
(needs-review) EmailCandidate. Idempotent on gmail_message_id. Safe to run on a schedule
and on-demand (manual Refresh).
"""

from __future__ import annotations

from datetime import datetime, timezone

from api.db.base import SessionLocal
from api.db.models import EmailCandidate
from api.services.audit import write_audit
from api.services import gmail_inbox
from api.settings import settings


def _to_dt(internal_ms: int | None) -> datetime | None:
    if not internal_ms:
        return None
    return datetime.fromtimestamp(internal_ms / 1000, tz=timezone.utc)


def ingest_offer_emails() -> dict:
    """Scan all configured mailboxes once. Returns a summary dict for logs/UI."""
    summary = {"scanned": 0, "ingested": 0, "skipped_seen": 0, "skipped_not_offer": 0, "mailboxes": 0}

    if not settings.ANTHROPIC_API_KEY:
        summary["error"] = "ANTHROPIC_API_KEY not configured"
        return summary

    services = gmail_inbox.build_inbox_services()
    summary["mailboxes"] = len(services)
    if not services:
        summary["error"] = "no mailbox tokens configured"
        return summary

    # Import here so a missing key / import issue can't break module load.
    from hr_assistant.claude_assistant import extract_offer_details

    query = f"from:{settings.OFFER_SENDER} newer_than:{settings.INGEST_LOOKBACK_DAYS}d"
    db = SessionLocal()
    try:
        for mailbox, gmail in services:
            try:
                ids = gmail_inbox.search_message_ids(gmail, query, max_results=50)
            except Exception:  # noqa: BLE001 — skip a mailbox that errors on search
                continue
            if not ids:
                continue

            # Dedup: which of these message ids are already stored?
            seen = {
                r[0] for r in db.query(EmailCandidate.gmail_message_id)
                .filter(EmailCandidate.gmail_message_id.in_(ids)).all()
            }

            for mid in ids:
                summary["scanned"] += 1
                if mid in seen:
                    summary["skipped_seen"] += 1
                    continue
                try:
                    msg = gmail_inbox.get_message(gmail, mid)
                    data = extract_offer_details(msg["subject"], msg["body"])
                except Exception:  # noqa: BLE001 — one bad message shouldn't abort the run
                    continue

                if not data.get("is_offer") or not (data.get("full_name") or "").strip():
                    summary["skipped_not_offer"] += 1
                    continue

                row = EmailCandidate(
                    source_mailbox=mailbox,
                    gmail_message_id=msg["id"],
                    gmail_thread_id=msg.get("thread_id"),
                    sender=msg.get("sender"),
                    subject=msg.get("subject"),
                    received_at=_to_dt(msg.get("internal_ms")),
                    full_name=(data.get("full_name") or "").strip() or None,
                    cnic=(data.get("cnic") or "").strip() or None,
                    personal_email=(data.get("personal_email") or "").strip() or None,
                    joining_date=(data.get("joining_date") or "").strip() or None,
                    gross_salary=(data.get("gross_salary") or "").strip() or None,
                    role=(data.get("role") or "").strip() or None,
                    department=(data.get("department") or "").strip() or None,
                    jd_text=(data.get("job_description") or "").strip() or None,
                    raw_extract=data,
                    status="new",
                )
                db.add(row)
                try:
                    db.commit()
                    summary["ingested"] += 1
                    write_audit(
                        db, settings.OFFER_SENDER, "EMAIL_CANDIDATE_INGESTED",
                        detail={"mailbox": mailbox, "name": row.full_name, "gmail_id": row.gmail_message_id},
                    )
                except Exception:  # noqa: BLE001 — unique-constraint race or bad row
                    db.rollback()
        return summary
    finally:
        db.close()
