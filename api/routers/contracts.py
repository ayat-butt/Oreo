"""Contract drafting endpoints — create (async), poll job, fetch request."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db.base import get_db
from api.db.models import AppUser, ContractRequest, EmailCandidate, GeneratedDoc, Job
from api.auth.deps import current_user
from api.schemas import (
    ContractCreate, CreateContractResponse, ContractRequestOut,
    GeneratedDocOut, JobOut,
)
from api.services.jobs import run_draft_job

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("", response_model=CreateContractResponse, status_code=201)
def create_contract(
    body: ContractCreate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: AppUser = Depends(current_user),
):
    """Validate the emp payload, persist a request + queued job, kick off background drafting."""
    # Idempotency: return the existing request on a repeated key.
    if body.idempotency_key:
        existing = db.query(ContractRequest).filter(
            ContractRequest.idempotency_key == body.idempotency_key
        ).one_or_none()
        if existing:
            job = db.query(Job).filter(Job.request_id == existing.id).order_by(Job.created_at.desc()).first()
            return CreateContractResponse(
                request_id=str(existing.id),
                job_id=str(job.id) if job else "",
                status=existing.status,
            )

    req = ContractRequest(
        created_by=user.id,
        markaz_application_id=body.markaz_application_id,
        candidate_snapshot=body.candidate_snapshot,
        emp_payload=body.emp.model_dump(),
        entity=body.emp.entity,
        employment_type=body.emp.employment_type,
        status="draft",
        idempotency_key=body.idempotency_key,
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    # If this draft came from an ingested offer email, link it and mark it drafted.
    if body.email_candidate_id:
        try:
            ec = db.get(EmailCandidate, uuid.UUID(body.email_candidate_id))
        except ValueError:
            ec = None
        if ec:
            ec.contract_request_id = req.id
            ec.status = "drafted"
            db.commit()

    job = Job(kind="draft_contract", request_id=req.id, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)

    background.add_task(run_draft_job, req.id, user.email)
    return CreateContractResponse(request_id=str(req.id), job_id=str(job.id), status="generating")


@router.get("/{request_id}", response_model=ContractRequestOut)
def get_contract(request_id: uuid.UUID, db: Session = Depends(get_db),
                 user: AppUser = Depends(current_user)):
    req = db.get(ContractRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="request not found")
    doc = db.query(GeneratedDoc).filter(GeneratedDoc.request_id == req.id).order_by(
        GeneratedDoc.created_at.desc()).first()
    job = db.query(Job).filter(Job.request_id == req.id).order_by(Job.created_at.desc()).first()
    return ContractRequestOut(
        id=str(req.id),
        status=req.status,
        entity=req.entity,
        employment_type=req.employment_type,
        markaz_application_id=req.markaz_application_id,
        docs=(GeneratedDocOut(
            folder_url=doc.folder_url, contract_url=doc.contract_url, nda_url=doc.nda_url,
            contract_id=doc.contract_id, nda_id=doc.nda_id, shared_with=doc.shared_with,
        ) if doc else None),
        job=(JobOut(id=str(job.id), kind=job.kind, status=job.status, error=job.error,
                    request_id=str(req.id)) if job else None),
    )


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db),
            user: AppUser = Depends(current_user)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobOut(id=str(job.id), kind=job.kind, status=job.status, error=job.error,
                  request_id=str(job.request_id) if job.request_id else None)
