"""Candidates (offer pipeline) — read-only from Markaz, grouped for the dashboard.

NOTE: auth is not yet wired (Phase 1 SSO). These endpoints will be protected by the
`current_user` dependency once the Google OAuth client exists.
"""

from collections import defaultdict
from fastapi import APIRouter, HTTPException

from hr_assistant import markaz_db
from api.schemas import CandidatesResponse, DepartmentGroup, PipelineCandidate, CandidateDetail
from api.services import enrichment

router = APIRouter(prefix="/candidates", tags=["candidates"])


def _to_card(row: dict) -> PipelineCandidate:
    legal = (row.get("legal_name") or "").strip()
    name = legal or f"{row.get('first_name') or ''} {row.get('last_name') or ''}".strip()
    return PipelineCandidate(
        application_id=row["application_id"],
        candidate_id=row.get("candidate_id"),
        job_id=row.get("job_id"),
        name=name or "(unnamed)",
        email=row.get("email"),
        department=row.get("job_department"),
        job_title=row.get("job_title"),
        status=row.get("status"),
        stage=row.get("stage"),
        ready_to_draft=bool(row.get("ready_to_draft")),
        cnic_present=bool(row.get("cnic")),
        job_employment_type=row.get("job_employment_type"),
        engine_employment_type=markaz_db.map_employment_type(row.get("job_employment_type")),
        updated_at=row.get("updated_at"),
    )


@router.get("", response_model=CandidatesResponse)
def list_candidates():
    """Offer/hired candidates grouped by department, ready-to-draft first."""
    rows = markaz_db.get_offer_pipeline()
    cards = [_to_card(r) for r in rows]

    groups: dict[str, list[PipelineCandidate]] = defaultdict(list)
    for c in cards:
        groups[c.department or "(no department)"].append(c)

    group_models = [
        DepartmentGroup(department=dept, count=len(items), candidates=items)
        for dept, items in sorted(groups.items())
    ]
    return CandidatesResponse(
        total=len(cards),
        ready_to_draft=sum(1 for c in cards if c.ready_to_draft),
        groups=group_models,
    )


@router.get("/{application_id}", response_model=CandidateDetail)
def candidate_detail(application_id: int):
    """Detail + engine-field prefill + what's still missing for the contract form."""
    row = markaz_db.get_application_detail(application_id)
    if not row:
        raise HTTPException(status_code=404, detail="application not found")
    return enrichment.build_detail(row)
