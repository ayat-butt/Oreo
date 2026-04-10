"""Gmail service — read, label, and draft replies for HR emails."""

import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from googleapiclient.discovery import Resource
from .config import HR_LABELS


def ensure_hr_labels(gmail: Resource) -> dict[str, str]:
    """Create HR labels in Gmail if they don't exist. Returns {name: id}."""
    existing = gmail.users().labels().list(userId="me").execute().get("labels", [])
    label_map = {lbl["name"]: lbl["id"] for lbl in existing}

    for label_name in HR_LABELS:
        if label_name not in label_map:
            body = {
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            }
            created = gmail.users().labels().create(userId="me", body=body).execute()
            label_map[label_name] = created["id"]
            print(f"  Created label: {label_name}")

    return label_map


def get_unread_emails(gmail: Resource, max_results: int = 20) -> list[dict]:
    """Fetch unread emails from inbox. Returns list of parsed email dicts."""
    results = gmail.users().messages().list(
        userId="me",
        q="is:unread in:inbox",
        maxResults=max_results,
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg_ref in messages:
        msg = gmail.users().messages().get(
            userId="me",
            id=msg_ref["id"],
            format="full",
        ).execute()
        emails.append(_parse_email(msg))

    return emails


def _parse_email(msg: dict) -> dict:
    """Parse a Gmail API message into a clean dict."""
    headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
    body = _extract_body(msg["payload"])

    return {
        "id": msg["id"],
        "thread_id": msg["threadId"],
        "subject": headers.get("Subject", "(no subject)"),
        "sender": headers.get("From", ""),
        "to": headers.get("To", ""),
        "date": headers.get("Date", ""),
        "body": body,
        "snippet": msg.get("snippet", ""),
        "label_ids": msg.get("labelIds", []),
    }


def _extract_body(payload: dict) -> str:
    """Recursively extract plain-text body from a Gmail payload."""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result

    return ""


def apply_label(gmail: Resource, message_id: str, label_id: str) -> None:
    """Apply a label to a Gmail message."""
    gmail.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]},
    ).execute()


def mark_as_read(gmail: Resource, message_id: str) -> None:
    """Remove UNREAD label from a message."""
    gmail.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()


def create_draft(gmail: Resource, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> dict:
    """Create a Gmail draft. Returns the created draft object."""
    message = MIMEMultipart("alternative")
    message["To"] = to
    message["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
    message.attach(MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    draft_body: dict = {"message": {"raw": raw}}
    if thread_id:
        draft_body["message"]["threadId"] = thread_id

    return gmail.users().drafts().create(userId="me", body=draft_body).execute()


def send_email(gmail: Resource, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> dict:
    """Send an email immediately. Returns the sent message."""
    message = MIMEMultipart("alternative")
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    send_body: dict = {"raw": raw}
    if thread_id:
        send_body["threadId"] = thread_id

    return gmail.users().messages().send(userId="me", body=send_body).execute()
