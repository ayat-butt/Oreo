"""Pydantic response/request models for the Contracts API."""

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, model_validator

from hr_assistant.contract_service import CONTRACT_PAIRS


class PipelineCandidate(BaseModel):
    """One row on the dashboard — an offer/hired application. No CNIC here (data hygiene)."""
    application_id: int
    candidate_id: int | None = None
    job_id: int | None = None
    name: str                      # legal name if submitted, else first+last
    email: str | None = None
    department: str | None = None
    job_title: str | None = None
    status: str                    # offer | hired
    stage: str | None = None
    ready_to_draft: bool           # legal name + CNIC submitted in Markaz
    cnic_present: bool             # whether Markaz already has the CNIC
    job_employment_type: str | None = None      # raw Markaz value (Permanent/Contractual)
    engine_employment_type: str | None = None    # mapped (full_time/project) or None
    updated_at: datetime | None = None


class DepartmentGroup(BaseModel):
    department: str
    count: int
    candidates: list[PipelineCandidate]


class CandidatesResponse(BaseModel):
    total: int
    ready_to_draft: int
    groups: list[DepartmentGroup]


class EmpPrefill(BaseModel):
    """Engine `emp` fields pre-filled from Markaz; the form fills the rest."""
    name: str | None = None
    cnic: str | None = None
    email: str | None = None
    designation: str | None = None
    department: str | None = None
    employment_type: str | None = None   # mapped from job; user confirms
    # Manual (not in pipeline) — surfaced as missing
    entity: str | None = None
    salary: str | None = None
    joining_date: str | None = None
    gender: str | None = None
    hod_name: str | None = None
    hod_designation: str | None = None
    jd_doc_id: str | None = None
    jd_text: str | None = None


class CandidateDetail(BaseModel):
    application_id: int
    status: str
    stage: str | None = None
    ready_to_draft: bool
    prefill: EmpPrefill
    missing_fields: list[str]
    hints: dict[str, str | None]         # e.g. hiring_manager, work_type, budget, jd_text presence


# ── Contract drafting (write) ────────────────────────────────────────────────

class EmpModel(BaseModel):
    """The engine `emp` dict, validated. Mirrors hr_assistant.contract_service requirements."""
    name: str
    cnic: str
    designation: str
    department: str
    salary: str
    joining_date: str
    entity: str               # owt | opl | taleemabad | orenda
    employment_type: str      # full_time | project | part_time | addendum
    gender: str | None = None
    # project / part_time
    start_date: str | None = None
    end_date: str | None = None
    duration: str | None = None
    # addendum
    prev_contract_date: str | None = None
    # signing / JD / clauses
    hod_name: str | None = None
    hod_designation: str | None = None
    direct_report: str | None = None        # project: "Direct Report to"
    indirect_report: str | None = None      # project: "Coordination & Indirect Report to"
    jd_doc_id: str | None = None
    jd_text: str | None = None            # pasted/Markaz JD text → Annexure-A
    is_transition: bool = False
    # joining arrangement (optional)
    remote_date: str | None = None
    inperson_date: str | None = None
    # welcome email
    email: str | None = None
    cc_list: list[str] | None = None

    @model_validator(mode="after")
    def _validate(self):
        if (self.entity, self.employment_type) not in CONTRACT_PAIRS:
            valid = sorted({f"{e}/{t}" for (e, t) in CONTRACT_PAIRS})
            raise ValueError(
                f"invalid entity/employment_type '{self.entity}/{self.employment_type}'. Valid: {valid}"
            )
        if self.employment_type in ("project", "part_time"):
            miss = [f for f in ("start_date", "end_date", "duration") if not getattr(self, f)]
            if miss:
                raise ValueError(f"{self.employment_type} requires: {miss}")
        if self.employment_type == "addendum":
            miss = [f for f in ("prev_contract_date", "end_date") if not getattr(self, f)]
            if miss:
                raise ValueError(f"addendum requires: {miss}")
        return self


class ContractCreate(BaseModel):
    emp: EmpModel
    markaz_application_id: int | None = None
    email_candidate_id: str | None = None       # link when drafting from an ingested offer email
    candidate_snapshot: dict | None = None
    idempotency_key: str | None = None


# ── Email-sourced candidates (ingested from offer emails) ─────────────────────

class EmailCandidateOut(BaseModel):
    """One card in the 'From Email' section."""
    id: str
    name: str | None = None
    role: str | None = None
    department: str | None = None
    personal_email: str | None = None
    gross_salary: str | None = None
    joining_date: str | None = None
    status: str                          # new (needs review) | drafted | dismissed
    source_mailbox: str | None = None
    sender: str | None = None
    subject: str | None = None
    received_at: datetime | None = None
    created_at: datetime | None = None


class EmailCandidatesResponse(BaseModel):
    total: int
    needs_review: int
    candidates: list[EmailCandidateOut]


class EmailCandidateDetail(BaseModel):
    id: str
    status: str
    source_mailbox: str | None = None
    sender: str | None = None
    subject: str | None = None
    received_at: datetime | None = None
    prefill: EmpPrefill
    missing_fields: list[str]
    hints: dict[str, str | None]


class AccessMemberOut(BaseModel):
    id: str
    email: str
    name: str | None = None
    is_admin: bool = False
    is_active: bool = True
    is_owner: bool = False          # owner rows can't be edited/removed
    created_at: datetime | None = None


class AccessListResponse(BaseModel):
    members: list[AccessMemberOut]


class AccessMemberCreate(BaseModel):
    email: str
    name: str | None = None


class AccessMemberUpdate(BaseModel):
    is_active: bool | None = None
    is_admin: bool | None = None


class IngestResult(BaseModel):
    scanned: int = 0
    ingested: int = 0
    skipped_seen: int = 0
    skipped_not_offer: int = 0
    mailboxes: int = 0
    error: str | None = None


class JobOut(BaseModel):
    id: str
    kind: str
    status: str                # queued | running | done | error
    error: str | None = None
    request_id: str | None = None


class GeneratedDocOut(BaseModel):
    folder_url: str | None = None
    contract_url: str | None = None
    nda_url: str | None = None
    contract_id: str | None = None
    nda_id: str | None = None
    shared_with: list[str] | None = None


class ContractRequestOut(BaseModel):
    id: str
    status: str                # draft | generating | preview | pilot_sent | sent | failed
    entity: str | None = None
    employment_type: str | None = None
    markaz_application_id: int | None = None
    docs: GeneratedDocOut | None = None
    job: JobOut | None = None


class CreateContractResponse(BaseModel):
    request_id: str
    job_id: str
    status: str


# ── Email (draft / pilot / live) ─────────────────────────────────────────────

class EmailDraftRequest(BaseModel):
    cc: list[str] | None = None


class EmailPilotRequest(BaseModel):
    test_address: str | None = None      # defaults to settings.TEST_PILOT_EMAIL
    cc: list[str] | None = None


class EmailLiveRequest(BaseModel):
    confirm: bool = False                # must be True to actually send to the candidate
    cc: list[str] | None = None


class EmailResult(BaseModel):
    kind: str                            # draft | pilot | live
    to: str
    subject: str
    gmail_id: str
    request_status: str


class EmailPreview(BaseModel):
    subject: str
    to: str | None = None
    cc: list[str] = []
    html_body: str
    attachments: list[str] = []
