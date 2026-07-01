"""Ingest offer-letter email THREADS into the app DB as email_candidates.

The offer details are split across a thread: the recruiter's offer message (role, employment
type, gross salary) and the candidate's reply (full name, CNIC, joining date). So we process
the whole thread, not a single message. For each configured mailbox we find recent threads
from the offer sender, flatten each thread, ask Claude to extract+merge the details, and
upsert a 'new' (needs-review) EmailCandidate. Idempotent on gmail_thread_id.

A thread that's still 'new' is re-extracted on later polls so a candidate's reply that arrives
after the first scan gets picked up. Threads already 'drafted'/'dismissed' are left alone.
"""

from __future__ import annotations

import re
import urllib.parse
from datetime import datetime, timezone

from googleapiclient.discovery import build
from sqlalchemy import func

from api.db.base import SessionLocal
from api.db.models import EmailCandidate
from api.services.audit import write_audit
from api.services import gmail_inbox
from api.settings import settings

_docs_service = None


def _docs():
    """Docs client (service identity) for reading a linked JD Google Doc. Cached."""
    global _docs_service
    if _docs_service is None:
        from hr_assistant.config import get_google_services
        _docs_service = get_google_services(allow_interactive=False)["docs"]
    return _docs_service


def _jd_doc_id_from_links(links) -> str | None:
    """Pick the Job Description Google-Doc id from the thread's links.
    Prefers an anchor whose text mentions JD / job description; else the first doc link."""
    cands: list[tuple[str, str]] = []
    for text, href in links or []:
        h = urllib.parse.unquote(href or "")          # Gmail often wraps links in google.com/url?q=…
        m = re.search(r"docs\.google\.com/document/d/([A-Za-z0-9_-]{20,})", h)
        if m:
            cands.append((text or "", m.group(1)))
    if not cands:
        return None
    for text, did in cands:
        if re.search(r"\bjd\b|job\s*desc", text, re.I):
            return did
    return cands[0][1]


def _markaz_jd_for_role(role: str | None) -> str:
    """Look up the JD in Markaz by role/designation (the canonical source — every JD lives
    there). Returns a clean Responsibilities-focused JD, or '' if no matching job."""
    if not role or not role.strip():
        return ""
    try:
        from hr_assistant import markaz_db
        from api.services.enrichment import jd_from_description
        row = markaz_db.get_job_jd_by_title(role)
        if not row:
            return ""
        jd = jd_from_description(row.get("description") or "")
        return jd or (row.get("jd_text") or "").strip()
    except Exception:  # noqa: BLE001
        return ""


def _read_jd(svc, doc_id: str) -> str:
    """Read + clean a JD doc with a specific Docs client (raises if it can't be read)."""
    from hr_assistant.contract_service import _extract_jd_lines
    items = _extract_jd_lines(svc, doc_id)
    if items:
        return "\n".join(t for t, _ in items)
    d = svc.documents().get(documentId=doc_id).execute()
    lines = ["".join(pe.get("textRun", {}).get("content", "")
                     for pe in el["paragraph"].get("elements", [])).rstrip()
             for el in d.get("body", {}).get("content", []) if "paragraph" in el]
    full = "\n".join(lines)
    from api.services.enrichment import _RESP_START, _RESP_END
    m = _RESP_START.search(full)
    if m:
        end = _RESP_END.search(full, m.end())
        section = full[m.start(): end.start() if end else len(full)].strip()
        if section:
            return section
    return "\n".join(l for l in lines if l.strip())


def _fetch_jd_text(doc_id: str, primary=None) -> str:
    """Read a linked JD doc → clean Responsibilities-focused JD.

    Tries the mailbox's own identity first (can open org-restricted docs), then the niete
    service identity; one retry each for transient API blips. '' if none can read it."""
    for svc in [s for s in (primary, _docs()) if s is not None]:
        for _attempt in range(2):
            try:
                txt = _read_jd(svc, doc_id)
                if txt:
                    return txt
                break  # readable but empty → don't retry this svc
            except Exception:  # noqa: BLE001 — no access / transient → try next
                continue
    return ""


def _is_cross_mailbox_duplicate(db, full_name: str | None, cnic: str | None) -> bool:
    """The same offer can land in both inboxes as separate threads. Treat as one candidate:
    skip if a non-dismissed row already has this CNIC, or (failing a CNIC) the same name."""
    base = db.query(EmailCandidate.id).filter(EmailCandidate.status != "dismissed")
    if cnic and base.filter(EmailCandidate.cnic == cnic).first():
        return True
    if full_name and base.filter(func.lower(EmailCandidate.full_name) == full_name.lower()).first():
        return True
    return False


def _to_dt(internal_ms: int | None) -> datetime | None:
    if not internal_ms:
        return None
    return datetime.fromtimestamp(internal_ms / 1000, tz=timezone.utc)


def _clean(v) -> str | None:
    return (v or "").strip() or None


def ingest_offer_emails() -> dict:
    """Scan all configured mailboxes once. Returns a summary dict for logs/UI."""
    summary = {"scanned": 0, "ingested": 0, "skipped_seen": 0, "skipped_not_offer": 0, "mailboxes": 0}

    services = gmail_inbox.build_inbox_services()
    summary["mailboxes"] = len(services)
    if not services:
        summary["error"] = "no mailbox tokens configured"
        return summary

    # Extraction: use Claude ONLY when a real Anthropic API key is present (sk-ant-api…).
    # Otherwise (or if Claude errors) fall back to deterministic rule-based parsing — so
    # ingestion never depends on a working Anthropic key.
    from api.services.offer_parser import extract_offer_details_rules
    _use_claude = settings.ANTHROPIC_API_KEY.startswith("sk-ant-api")

    def extract(subj: str, body: str) -> dict:
        if _use_claude:
            try:
                from hr_assistant.claude_assistant import extract_offer_details
                return extract_offer_details(subj, body)
            except Exception as e:  # noqa: BLE001 — bad key / API error → rules fallback
                extract_errors.append(f"claude: {type(e).__name__}: {e}")
        return extract_offer_details_rules(subj, body)

    senders = settings.offer_senders
    if not senders:
        summary["error"] = "no offer senders configured"
        return summary
    from_clause = " OR ".join(f"from:{s}" for s in senders)
    parts = [f"({from_clause})"]
    if settings.OFFER_SUBJECT.strip():
        parts.append(f'subject:"{settings.OFFER_SUBJECT.strip()}"')
    if settings.INGEST_SINCE.strip():
        parts.append(f"after:{settings.INGEST_SINCE.strip()}")   # backfill from a fixed date
    else:
        parts.append(f"newer_than:{settings.INGEST_LOOKBACK_DAYS}d")
    query = " ".join(parts)
    extract_errors: list[str] = []
    db = SessionLocal()
    try:
        for mailbox, gmail, creds in services:
            try:
                mbox_docs = build("docs", "v1", credentials=creds, cache_discovery=False)
            except Exception:  # noqa: BLE001
                mbox_docs = None
            try:
                thread_ids = gmail_inbox.search_thread_ids(gmail, query, max_results=100)
            except Exception:  # noqa: BLE001 — skip a mailbox that errors on search
                continue
            if not thread_ids:
                continue

            existing = {
                r.gmail_thread_id: r for r in db.query(EmailCandidate)
                .filter(EmailCandidate.gmail_thread_id.in_(thread_ids)).all()
            }

            for tid in thread_ids:
                summary["scanned"] += 1
                row = existing.get(tid)
                # Already acted on (drafted/dismissed) → leave it; only refresh ones still 'new'.
                if row and row.status != "new":
                    summary["skipped_seen"] += 1
                    continue

                try:
                    th = gmail_inbox.get_thread(gmail, tid)
                    data = extract(th["subject"], th["text"])
                except Exception as e:  # noqa: BLE001 — one bad thread shouldn't abort the run
                    extract_errors.append(f"{type(e).__name__}: {e}")
                    continue

                if not data.get("is_offer") or not (data.get("full_name") or "").strip():
                    summary["skipped_not_offer"] += 1
                    continue

                # JD source priority: inline text → Markaz by role (canonical, always
                # accessible) → the JD doc linked in the email ("Sharing the JD …").
                jd_text_val = _clean(data.get("job_description"))
                if not jd_text_val:
                    jd_text_val = _clean(_markaz_jd_for_role(data.get("role")))
                if not jd_text_val:
                    jd_doc_id = _jd_doc_id_from_links(th.get("links"))
                    if jd_doc_id:
                        jd_text_val = _clean(_fetch_jd_text(jd_doc_id, mbox_docs))

                participants = th.get("participants", "")
                who = next((s for s in senders if s in participants), senders[0])
                fields = dict(
                    source_mailbox=mailbox,
                    gmail_message_id=th.get("anchor_message_id"),
                    sender=who,
                    subject=th.get("subject"),
                    received_at=_to_dt(th.get("last_ms")),
                    full_name=_clean(data.get("full_name")),
                    cnic=_clean(data.get("cnic")),
                    personal_email=_clean(data.get("personal_email")),
                    joining_date=_clean(data.get("joining_date")),
                    gross_salary=_clean(data.get("gross_salary")),
                    role=_clean(data.get("role")),
                    department=_clean(data.get("department")),
                    employment_type=_clean(data.get("employment_type")),
                    jd_text=jd_text_val,
                    raw_extract=data,
                )

                if row:  # refresh a still-pending record (e.g. candidate replied after first scan)
                    for k, v in fields.items():
                        setattr(row, k, v)
                    try:
                        db.commit()
                    except Exception:  # noqa: BLE001
                        db.rollback()
                    continue

                # Same person already ingested from the other mailbox → don't duplicate.
                if _is_cross_mailbox_duplicate(db, fields["full_name"], fields["cnic"]):
                    summary["skipped_seen"] += 1
                    continue

                db.add(EmailCandidate(gmail_thread_id=tid, status="new", **fields))
                try:
                    db.commit()
                    summary["ingested"] += 1
                    write_audit(
                        db, settings.OFFER_SENDER, "EMAIL_CANDIDATE_INGESTED",
                        detail={"mailbox": mailbox, "name": fields["full_name"], "thread_id": tid},
                    )
                except Exception:  # noqa: BLE001 — unique-constraint race or bad row
                    db.rollback()

        # Surface a meaningful message if we matched threads but extracted nothing.
        if summary["ingested"] == 0 and extract_errors:
            summary["error"] = "extraction failed: " + extract_errors[0][:300]
        return summary
    finally:
        db.close()
