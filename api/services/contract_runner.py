"""Thin web wrapper around the locked contract engine.

Reuses hr_assistant.contract_service.draft_contracts() verbatim (no formatting changes),
runs it headless as the service identity, and re-extracts doc IDs from the returned URLs
(the engine returns URLs only).
"""

from __future__ import annotations

from hr_assistant.config import get_google_services
from hr_assistant.contract_service import draft_contracts


def _id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    try:
        return url.split("/d/")[1].split("/")[0]
    except (IndexError, AttributeError):
        return None


def run_draft(emp: dict) -> dict:
    """Generate contract (+NDA) for `emp` and return URLs + extracted IDs.

    Runs as the service identity (ayat@niete.edu.pk) with interactive auth disabled.
    """
    svcs = get_google_services(allow_interactive=False)
    # Drop None-valued keys so the engine's emp.get(field, "") defaults apply.
    # (e.g. gender=None would crash _salutation's None.lower(); absent → defaults to "Mr.")
    clean = {k: v for k, v in emp.items() if v is not None}
    res = draft_contracts(svcs["drive"], svcs["docs"], clean)
    folder_url = res.get("folder_url") or ""
    folder_id = folder_url.split("/folders/")[1].split("?")[0] if "/folders/" in folder_url else None
    return {
        **res,
        "contract_id": _id_from_url(res.get("contract_url")),
        "nda_id": _id_from_url(res.get("nda_url")),
        "folder_id": folder_id,
    }
