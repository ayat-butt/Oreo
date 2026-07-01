"""Deterministic (no-LLM) extractor for offer-email threads.

A fallback for the Claude extractor so ingestion works without an Anthropic API key.
Offer threads are structured enough to parse with rules:
  - the recruiter/HR message gives role, employment type, gross salary, joining date;
  - the candidate's reply gives "Full Name:" / "Name:" and "CNIC:";
  - a P&C forward may add "reporting to X" and "region X".
Anything it can't find comes back "" — the human review gate fills the rest.
"""

from __future__ import annotations

import re

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
_COMPANY_DOMAINS = ("taleemabad.com", "niete.edu.pk", "niete.pk")


def _first(pattern: str, text: str, group: int = 1) -> str:
    m = re.search(pattern, text, re.I)
    return (m.group(group) or "").strip() if m else ""


def _parse_date(s: str) -> str:
    """'23 July 2026' / '18th May 2026' / 'July 23, 2026' → '2026-07-23'. '' if no full date."""
    if not s:
        return ""
    m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})", s)
    if not m:
        m2 = re.search(r"([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", s)
        if not m2:
            return ""
        mon, day, yr = _MONTHS.get(m2.group(1).lower()), int(m2.group(2)), m2.group(3)
    else:
        day, mon, yr = int(m.group(1)), _MONTHS.get(m.group(2).lower()), m.group(3)
    if not mon:
        return ""
    return f"{yr}-{mon:02d}-{int(day):02d}"


def extract_offer_details_rules(subject: str, body: str) -> dict:
    text = f"{subject}\n{body}"

    full_name = (_first(r"Full Name\s*[:\-]\s*([^\n\r]+)", text)
                 or _first(r"(?:^|\n)\s*Name\s*[:\-]\s*([^\n\r]+)", text))
    # Fallback: subject often ends with "... | Candidate Name"
    if not full_name and "|" in subject:
        full_name = subject.rsplit("|", 1)[-1].strip()
    full_name = re.sub(r"[*_`]", "", full_name)
    full_name = re.sub(r"\s{2,}", " ", full_name).strip(" .,-")

    cnic_raw = _first(r"CNIC(?:\s*(?:No\.?|Number|#))?\s*[:\-]?\s*([0-9][0-9\-\s]{11,18}[0-9])", text)
    cnic = re.sub(r"\s", "", cnic_raw)

    emails = re.findall(r"[\w.\-]+@[\w.\-]+\.\w+", text)
    personal_email = next((e for e in emails if not e.lower().endswith(_COMPANY_DOMAINS)), "")

    jd_ctx = (_first(r"[Jj]oining [Dd]ate\s*[:\-]?\s*([^\n\r.]+)", text)
              or _first(r"joining date (?:is|will be|of)\s*([^\n\r.]+)", text)
              or _first(r"(?:start|commence|join)[^\n\r]{0,30}?(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]{3,9}\s+\d{4})", text))
    joining_date = _parse_date(jd_ctx) or _parse_date(text)

    gross_salary = re.sub(r"[,\s]", "", _first(r"PKR\s*([\d,\s]{3,})", text))

    role = (_first(r"(?:position|role)\s+of\s+(?:the\s+)?([^\n\r(,.]+?)(?:\s+at\s+|\s*\(|,|\.)", text)
            or _first(r"Offer Letter\s*[-–:]\s*([^\n\r|]+?)(?:\s+at\s+|\s*\|)", text)
            or _first(r"Offer Letter\s+([^\n\r|]+?)(?:\s*[-–]\s*at|\s+at\s+|\s*\|)", text))
    role = re.sub(r"[*_`]", "", role).strip(" -")

    et = ""
    if re.search(r"contractual|fixed[- ]term|\bproject\b|contract (?:ending|end|period)", text, re.I):
        et = "project"
    elif re.search(r"permanent|full[- ]time", text, re.I):
        et = "full_time"
    if re.search(r"part[- ]time", text, re.I):
        et = "part_time"

    reporting_to = _first(r"reporting to\s+([^\n\r,.]+?)(?:\s+and\b|,|\.|\n)", text)
    region = _first(r"(?:in\s+)?region\s+([A-Za-z][\w\- ]{1,30}?)(?:\.|,|\n|\s+and\s)", text)

    is_offer = bool(full_name) and bool(cnic or gross_salary or joining_date) and \
        bool(re.search(r"offer|accept|join|hire|position|role|contract", text, re.I))

    return {
        "is_offer": is_offer,
        "full_name": full_name,
        "cnic": cnic,
        "personal_email": personal_email,
        "joining_date": joining_date,
        "gross_salary": gross_salary,
        "role": role,
        "department": "",
        "employment_type": et,
        "reporting_to": reporting_to,
        "region": region,
        "job_description": "",
    }
