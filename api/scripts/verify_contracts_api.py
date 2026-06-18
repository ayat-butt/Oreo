"""Verify the contracts backend wiring WITHOUT running the 40s engine.

- app imports + routes register
- EmpModel validation (valid + invalid pair + missing project fields)
- DB persistence + GET /contracts/{id} via TestClient (dev-auth stub)
Cleans up the rows it creates.
"""

from fastapi.testclient import TestClient

from api.main import app
from api.db.base import SessionLocal
from api.db.models import ContractRequest, GeneratedDoc, Job, AuditEvent
from api.schemas import EmpModel

print("== routes ==")
for r in app.routes:
    methods = ",".join(sorted(getattr(r, "methods", []) or []))
    if getattr(r, "path", "").startswith(("/candidates", "/contracts", "/healthz")):
        print(f"  {methods:10} {r.path}")

print("\n== EmpModel validation ==")
ok = EmpModel(name="A B", cnic="1", designation="X", department="Y", salary="1",
              joining_date="1 July 2026", entity="taleemabad", employment_type="full_time")
print("  valid taleemabad/full_time: OK")
for bad in [
    dict(entity="orenda", employment_type="full_time"),       # invalid pair
    dict(entity="opl", employment_type="project"),            # missing start/end/duration
]:
    try:
        EmpModel(name="A", cnic="1", designation="X", department="Y", salary="1",
                 joining_date="d", **bad)
        print(f"  {bad}: NO ERROR (unexpected!)")
    except Exception as e:
        print(f"  {bad}: rejected -> {str(e).splitlines()[-1][:70]}")

print("\n== DB persistence + GET /contracts/{id} ==")
db = SessionLocal()
req = ContractRequest(emp_payload=ok.model_dump(), entity="taleemabad",
                      employment_type="full_time", status="preview")
db.add(req); db.commit(); db.refresh(req)
job = Job(kind="draft_contract", request_id=req.id, status="done")
db.add(job)
db.add(GeneratedDoc(request_id=req.id, contract_url="https://docs.google.com/document/d/TESTID/edit",
                    contract_id="TESTID", folder_url="https://drive.google.com/drive/folders/FID"))
db.commit()
rid = req.id

client = TestClient(app)
resp = client.get(f"/contracts/{rid}", headers={"X-Dev-User": "verify@taleemabad.com"})
print("  GET status:", resp.status_code)
print("  body:", resp.json())

# cleanup
db.query(GeneratedDoc).filter(GeneratedDoc.request_id == rid).delete()
db.query(Job).filter(Job.request_id == rid).delete()
db.query(AuditEvent).filter(AuditEvent.request_id == rid).delete()
db.query(ContractRequest).filter(ContractRequest.id == rid).delete()
db.commit()
db.close()
print("  cleaned up test rows: OK")
