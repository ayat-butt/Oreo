"""Turn a Markaz application row into engine-field prefill + a list of what's still missing.

Markaz auto-provides: name, cnic (when submitted), email, designation, department, employment_type.
Manual (must be entered in the form): entity, salary, joining_date, gender, hod_*, jd_doc_id.
"""

from __future__ import annotations

import re
import html as _html

from hr_assistant import markaz_db
from api.schemas import EmpPrefill, CandidateDetail

# Fields the engine needs that Markaz never has at offer stage → always manual.
ALWAYS_MANUAL = ["entity", "salary", "joining_date", "gender", "hod_name", "hod_designation"]

# JD extraction from the Markaz job posting (jobs.description is full HTML).
_RESP_START = re.compile(
    r"(?i)(key responsibilities|responsibilities|role overview|what you.?ll do|duties|your role|the role)"
)
_RESP_END = re.compile(
    r"(?i)(requirements|qualifications|what you.?ll bring|what we.?re looking|about you|"
    r"skills (and|&)|eligibility|experience required|benefits|perks|how to apply|compensation|we offer)"
)
_FIXES = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "�": "'", "\xa0": " ",
}


def _clean_html(h: str) -> str:
    if not h:
        return ""
    t = re.sub(r"<\s*(p|br|div|li|h[1-6]|tr|ul|ol)[^>]*>", "\n", h, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = _html.unescape(t)
    for a, b in _FIXES.items():
        t = t.replace(a, b)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def jd_from_description(description: str | None) -> str:
    """Clean the Markaz job posting and extract its Responsibilities section (full text if none found)."""
    txt = _clean_html(description or "")
    if not txt:
        return ""
    m = _RESP_START.search(txt)
    if not m:
        return txt
    end = _RESP_END.search(txt, m.end())
    section = txt[m.start(): end.start() if end else len(txt)].strip()
    return section or txt


def _full_name(row: dict) -> str | None:
    legal = (row.get("legal_name") or "").strip()
    if legal:
        return legal
    fn, ln = (row.get("first_name") or "").strip(), (row.get("last_name") or "").strip()
    return (fn + " " + ln).strip() or None


def build_prefill(row: dict) -> EmpPrefill:
    """Map a get_application_detail / get_offer_pipeline row to engine fields."""
    return EmpPrefill(
        name=_full_name(row),
        cnic=row.get("cnic") or None,
        email=row.get("email") or None,
        designation=row.get("job_title") or None,
        department=row.get("job_department") or None,
        employment_type=markaz_db.map_employment_type(row.get("job_employment_type")),
        # JD prefilled from the Markaz job posting (description), responsibilities section extracted.
        jd_text=(jd_from_description(row.get("job_description")) or (row.get("jd_text") or None)),
    )


def missing_fields(prefill: EmpPrefill) -> list[str]:
    """Engine-required fields not satisfied by Markaz prefill."""
    missing: list[str] = []
    if not prefill.name:
        missing.append("name")
    if not prefill.cnic:
        missing.append("cnic")
    if not prefill.designation:
        missing.append("designation")
    if not prefill.department:
        missing.append("department")
    if not prefill.employment_type:
        missing.append("employment_type")
    # always-manual fields
    missing.extend(ALWAYS_MANUAL)
    return missing


def build_detail(row: dict) -> CandidateDetail:
    prefill = build_prefill(row)
    return CandidateDetail(
        application_id=row["application_id"],
        status=row.get("status"),
        stage=row.get("stage"),
        ready_to_draft=bool(row.get("contract_submitted_at")),
        prefill=prefill,
        missing_fields=missing_fields(prefill),
        hints={
            "hiring_manager": row.get("hiring_manager"),
            "poc_person": row.get("poc_person"),
            "work_type": row.get("job_work_type"),
            "budget": (f"{row.get('min_budget')}-{row.get('max_budget')} {row.get('currency')}"
                       if row.get("min_budget") or row.get("max_budget") else None),
            "jd_text_available": "yes" if (row.get("jd_text") or "").strip() else "no",
        },
    )
