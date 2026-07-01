"""Multi-mailbox Gmail access for offer-email ingestion.

The rest of the app uses one service identity (ayat@niete.edu.pk via GOOGLE_SERVICE_TOKEN_JSON).
Offer emails can land in EITHER ayat@niete.edu.pk OR ayat@taleemabad.com, so this module builds a
read-only Gmail client per configured mailbox token and exposes a robust text-body extractor.

Tokens are authorized_user JSON blobs (same format as token.json), provided via env:
  - GMAIL_TOKEN_NIETE_JSON       (falls back to GOOGLE_SERVICE_TOKEN_JSON)
  - GMAIL_TOKEN_TALEEMABAD_JSON  (mint once with connect_mailbox.py)
"""

from __future__ import annotations

import base64
import html as _html
import json
import re

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from api.settings import settings


def build_inbox_services() -> list[tuple[str, object]]:
    """Return [(mailbox_email, gmail_service), ...] for every configured mailbox token.

    Silently skips mailboxes whose token is missing or unusable so one broken token never
    stops the others. Never blocks on interactive auth (web/Railway context).
    """
    services: list[tuple[str, object]] = []
    for mailbox, blob in settings.inbox_tokens.items():
        try:
            creds = Credentials.from_authorized_user_info(json.loads(blob))
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    continue
            gmail = build("gmail", "v1", credentials=creds, cache_discovery=False)
            services.append((mailbox, gmail))
        except Exception:  # noqa: BLE001 — a bad token must not break the loop
            continue
    return services


def search_thread_ids(gmail, query: str, max_results: int = 50) -> list[str]:
    """Return thread ids matching a Gmail query (newest first)."""
    res = gmail.users().threads().list(userId="me", q=query, maxResults=max_results).execute()
    return [t["id"] for t in res.get("threads", [])]


def get_thread(gmail, thread_id: str) -> dict:
    """Fetch a full thread and flatten every message into one text blob for extraction.

    The offer details span multiple messages (recruiter's offer + the candidate's reply
    with name/CNIC/joining date), so we concatenate all of them, each labelled by sender.
    Returns {thread_id, anchor_message_id, subject, participants, last_ms, message_count, text}.
    """
    th = gmail.users().threads().get(userId="me", id=thread_id, format="full").execute()
    msgs = th.get("messages", [])
    subject = ""
    anchor_id = None
    last_ms = 0
    participants: list[str] = []
    parts: list[str] = []
    for m in msgs:
        headers = {h["name"].lower(): h["value"] for h in m["payload"].get("headers", [])}
        if not subject:
            subject = headers.get("subject", "")
        frm = headers.get("from", "")
        if frm and frm not in participants:
            participants.append(frm)
        last_ms = max(last_ms, int(m.get("internalDate", 0) or 0))
        if anchor_id is None:
            anchor_id = m["id"]
        body = _extract_text_body(m["payload"])
        parts.append(f"--- Message from: {frm} ---\n{body}".strip())
    return {
        "thread_id": thread_id,
        "anchor_message_id": anchor_id,
        "subject": subject or "(no subject)",
        "participants": ", ".join(participants),
        "last_ms": last_ms or None,
        "message_count": len(msgs),
        "text": "\n\n".join(parts).strip(),
    }


_TAG_BREAKS = re.compile(r"(?i)<\s*(p|br|div|li|h[1-6]|tr|ul|ol)[^>]*>")
_TAGS = re.compile(r"<[^>]+>")


def _decode(data: str) -> str:
    if not data:
        return ""
    return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")


def _html_to_text(h: str) -> str:
    t = _TAG_BREAKS.sub("\n", h)
    t = _TAGS.sub("", t)
    t = _html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def _extract_text_body(payload: dict) -> str:
    """Prefer text/plain; fall back to text/html (stripped). Walks nested multiparts."""
    plain = _walk(payload, "text/plain")
    if plain.strip():
        return plain
    raw_html = _walk(payload, "text/html")
    return _html_to_text(raw_html) if raw_html.strip() else ""


def _walk(payload: dict, want_mime: str) -> str:
    if payload.get("mimeType") == want_mime:
        return _decode(payload.get("body", {}).get("data", ""))
    for part in payload.get("parts", []):
        found = _walk(part, want_mime)
        if found:
            return found
    return ""
