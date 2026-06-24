"""Thin web wrapper around the locked contract engine.

Reuses hr_assistant.contract_service.draft_contracts() verbatim (no formatting changes),
runs it headless as the service identity, and re-extracts doc IDs from the returned URLs
(the engine returns URLs only).
"""

from __future__ import annotations

from hr_assistant.config import get_google_services
from hr_assistant.contract_service import draft_contracts
from api.settings import settings


def _id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    try:
        return url.split("/d/")[1].split("/")[0]
    except (IndexError, AttributeError):
        return None


def _share_with_team(drive, file_ids: list[str | None]) -> list[str]:
    """Grant each P&C allowlist member writer access to the contract files (no email spam).

    Belt-and-suspenders on top of the shared parent folder, so the docs always open
    directly for the team even if folder inheritance is ever disrupted.
    """
    emails = sorted(settings.allowlist)
    for fid in [f for f in file_ids if f]:
        for email in emails:
            try:
                drive.permissions().create(
                    fileId=fid,
                    body={"type": "user", "role": "writer", "emailAddress": email},
                    sendNotificationEmail=False,
                    supportsAllDrives=True,
                ).execute()
            except Exception:  # noqa: BLE001 — never fail a draft over a share hiccup
                pass
    return emails


def run_draft(emp: dict) -> dict:
    """Generate contract (+NDA) for `emp` and return URLs + extracted IDs.

    Runs as the service identity (ayat@niete.edu.pk) with interactive auth disabled.
    """
    svcs = get_google_services(allow_interactive=False)
    drive = svcs["drive"]
    # Drop None-valued keys so the engine's emp.get(field, "") defaults apply.
    # (e.g. gender=None would crash _salutation's None.lower(); absent → defaults to "Mr.")
    clean = {k: v for k, v in emp.items() if v is not None}
    res = draft_contracts(drive, svcs["docs"], clean)
    folder_url = res.get("folder_url") or ""
    folder_id = folder_url.split("/folders/")[1].split("?")[0] if "/folders/" in folder_url else None
    contract_id = _id_from_url(res.get("contract_url"))
    nda_id = _id_from_url(res.get("nda_url"))
    shared_with = _share_with_team(drive, [folder_id, contract_id, nda_id])
    return {
        **res,
        "contract_id": contract_id,
        "nda_id": nda_id,
        "folder_id": folder_id,
        "shared_with": shared_with,
    }
