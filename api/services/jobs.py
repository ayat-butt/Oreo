"""Background draft-generation job.

draft_contracts() takes ~40s of sequential Google API calls, so it runs off the request
thread (FastAPI BackgroundTasks → threadpool). The frontend polls GET /jobs/{id}.
A small semaphore protects the single shared service identity's API quota.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone

from api.db.base import SessionLocal
from api.db.models import ContractRequest, GeneratedDoc, Job
from api.services.contract_runner import run_draft
from api.services.audit import write_audit

# Cap concurrent drafts (one shared Google identity).
_DRAFT_SEMAPHORE = threading.Semaphore(2)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def run_draft_job(request_id: uuid.UUID, actor_email: str | None) -> None:
    """Execute one draft job. Runs in a worker thread; owns its own DB session."""
    db = SessionLocal()
    job = (
        db.query(Job)
        .filter(Job.request_id == request_id, Job.kind == "draft_contract")
        .order_by(Job.created_at.desc())
        .first()
    )
    req = db.get(ContractRequest, request_id)
    if job is None or req is None:
        db.close()
        return

    acquired = _DRAFT_SEMAPHORE.acquire(timeout=300)
    try:
        job.status = "running"
        job.started_at = _now()
        req.status = "generating"
        db.commit()

        result = run_draft(req.emp_payload)

        db.add(GeneratedDoc(
            request_id=req.id,
            folder_id=result.get("folder_id"),
            folder_url=result.get("folder_url"),
            contract_id=result.get("contract_id"),
            contract_url=result.get("contract_url"),
            nda_id=result.get("nda_id"),
            nda_url=result.get("nda_url"),
            shared_with=result.get("shared_with"),
        ))
        req.status = "preview"
        job.status = "done"
        job.finished_at = _now()
        job.result = {k: result.get(k) for k in
                      ("folder_url", "contract_url", "nda_url", "contract_id", "nda_id")}
        db.commit()
        write_audit(db, actor_email, "CONTRACT_DRAFTED", request_id=req.id,
                    detail={"entity": req.entity, "employment_type": req.employment_type,
                            "contract_id": result.get("contract_id"), "nda_id": result.get("nda_id")})
    except Exception as e:  # noqa: BLE001
        db.rollback()
        try:
            job.status = "error"
            job.error = f"{type(e).__name__}: {e}"
            job.finished_at = _now()
            req.status = "failed"
            db.commit()
            write_audit(db, actor_email, "CONTRACT_DRAFT_FAILED", request_id=req.id,
                        detail={"error": str(e)[:500]})
        except Exception:
            db.rollback()
    finally:
        if acquired:
            _DRAFT_SEMAPHORE.release()
        db.close()
