"""Claude-powered HR intelligence — categorize emails, draft replies, generate documents."""

import json
from typing import Optional
import anthropic
from .config import ANTHROPIC_API_KEY, COMPANY_NAME, CATEGORY_KEYWORDS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = f"""You are an expert HR assistant for {COMPANY_NAME}. You help HR managers by:
- Categorizing emails into: Contracts, Benefits, Payroll, or Employee Queries
- Drafting professional, empathetic, and compliant HR responses
- Generating HR documents (contracts, onboarding materials, policy letters)
- Extracting calendar event details from emails

Always be professional, clear, and HR-best-practices compliant.
Never include confidential information beyond what is necessary.
Sign off with "HR Team, {COMPANY_NAME}" unless instructed otherwise."""


def categorize_email(subject: str, body: str, sender: str) -> dict:
    """
    Use Claude to categorize an email into an HR label and assess priority.
    Returns: {"category": str, "priority": str, "reason": str}
    """
    prompt = f"""Analyze this email and categorize it for an HR team.

From: {sender}
Subject: {subject}
Body:
{body[:2000]}

Respond with valid JSON only:
{{
  "category": "<one of: HR/Contracts | HR/Benefits | HR/Payroll | HR/Employee-Queries>",
  "priority": "<one of: high | medium | low>",
  "reason": "<one sentence explaining your classification>"
}}"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


def draft_reply(subject: str, body: str, sender: str, category: str) -> str:
    """Draft a professional HR reply to an email."""
    prompt = f"""Draft a professional HR email reply to this message.

Category: {category}
From: {sender}
Subject: {subject}
Original message:
{body[:3000]}

Requirements:
- Professional and empathetic tone
- Address the sender's specific concern
- Be concise (under 250 words)
- Include next steps if applicable
- End with "Best regards,\\nHR Team, {COMPANY_NAME}"

Write only the email body text, no subject line."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "text":
            return block.text.strip()
    return ""


def extract_calendar_event(subject: str, body: str) -> Optional[dict]:
    """
    Extract meeting/event details from an email if present.
    Returns a dict with event details, or None if no event found.
    """
    prompt = f"""Examine this email and determine if it requests or mentions a meeting, interview, or scheduled event.

Subject: {subject}
Body:
{body[:2000]}

If an event is found, respond with JSON:
{{
  "found": true,
  "title": "<event title>",
  "description": "<brief description>",
  "date": "<YYYY-MM-DD or 'unspecified'>",
  "time": "<HH:MM in 24h or 'unspecified'>",
  "duration_minutes": <integer or 60>,
  "attendees": ["<email addresses if mentioned>"],
  "location": "<location or 'Virtual' or ''>"
}}

If NO event is found, respond with: {{"found": false}}

Respond with valid JSON only."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    result = json.loads(text)
    return result if result.get("found") else None


def generate_hr_document(doc_type: str, details: dict) -> dict:
    """
    Generate an HR document using Claude.

    Args:
        doc_type: One of "offer_letter", "onboarding", "contract", "policy_update", "custom"
        details: Context dict (employee name, position, salary, start date, etc.)

    Returns: {"title": str, "content": str}
    """
    templates = {
        "offer_letter": "a formal job offer letter",
        "onboarding": "a new employee onboarding welcome letter with first-day instructions",
        "contract": "an employment contract with standard clauses",
        "policy_update": "an HR policy update announcement",
        "custom": "an HR document",
    }
    description = templates.get(doc_type, templates["custom"])

    detail_str = "\n".join(f"  {k}: {v}" for k, v in details.items())

    prompt = f"""Generate {description} for {COMPANY_NAME}.

Details provided:
{detail_str}

Write a complete, professional document with:
- Appropriate header/title
- All standard sections for this document type
- Professional language
- Placeholder brackets [PLACEHOLDER] for any fields not provided
- Company name: {COMPANY_NAME}

Return the full document text."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    content = ""
    for block in response.content:
        if block.type == "text":
            content = block.text.strip()
            break

    doc_type_titles = {
        "offer_letter": "Offer Letter",
        "onboarding": "Onboarding Welcome",
        "contract": "Employment Contract",
        "policy_update": "Policy Update",
        "custom": "HR Document",
    }
    employee = details.get("employee_name", details.get("name", ""))
    title_prefix = doc_type_titles.get(doc_type, "HR Document")
    title = f"{title_prefix} — {employee}" if employee else title_prefix

    return {"title": title, "content": content}


def summarize_email_batch(emails: list[dict]) -> str:
    """Produce a concise summary of multiple emails for an HR manager briefing."""
    if not emails:
        return "No emails to summarize."

    email_list = "\n\n".join(
        f"Email {i+1}:\n  From: {e['sender']}\n  Subject: {e['subject']}\n  Snippet: {e['snippet']}"
        for i, e in enumerate(emails)
    )

    prompt = f"""Summarize these {len(emails)} HR emails for a manager briefing.
Highlight urgent items, common themes, and recommended actions.

{email_list}

Format as:
- Urgent (🔴): ...
- Medium priority (🟡): ...
- Low priority (🟢): ...
- Recommended actions: ..."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "text":
            return block.text.strip()
    return ""
