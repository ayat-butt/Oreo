# Phase 0 — Markaz Verification Findings (read-only)

Date: 2026-06-17. Verified live against `MARKAZ_DB_URL` with read-only queries
(`api/scripts/verify_markaz*.py`). Markaz = Postgres on Neon, 63 tables.

## The hiring pipeline lives in `applications`, NOT `candidates`

- **`candidates`** (2,788 rows) = raw applicant pool from the career page (resume, AI scores).
  It has **no `status` column** — so the existing `markaz_db.get_candidates(status=...)` is
  effectively broken/unused for our purposes. Holds only: first_name, last_name, email, phone,
  position (mostly null), area_of_interest, university, semester.
- **`applications`** (3,463 rows) = the pipeline. Links `candidate_id → job_id` with `status` + `stage`.
  - `status` values: `new` (1908), `rejected` (1124), `shortlisted` (288), `case_study_sent` (40),
    **`offer` (36)**, **`hired` (20)**, `P2` (15), `warm_bench` (14), `applied` (8), `gwc_scheduled` (6),
    `consider_other_roles` (3), `withdrawn` (1).
  - **Contract-drafting columns already exist on `applications`:**
    - `contract_drafting_full_legal_name` (text) — the candidate's legal name
    - `contract_drafting_cnic_number` (text) — CNIC
    - `contract_drafting_submitted_at` (timestamp) — **the "accepted + ready to draft" signal**
  - Of 56 offer/hired applications, **7** have these filled. So when present we get name+CNIC free;
    otherwise manual.
- **`status_transitions`** defines a configured workflow status literal **`"Contract Drafting"`** —
  Markaz already models a contract-drafting handoff stage.

## Dashboard data source (decided)

The Dashboard = `applications` where `status IN ('offer','hired')`, joined to `candidates` (name/email)
and `jobs` (title/department/employment_type/jd_text/budget), grouped by `jobs.department` then `jobs.title`.

"Ready to draft" badge = `contract_drafting_submitted_at IS NOT NULL` (candidate accepted & gave legal
details). This realizes the user's "Dashboard (Offer Acceptance) → e.g. Program → Yumna Sohail → Proceed".

## Candidate → engine `emp` field mapping (final)

Engine requires: name, cnic, designation, department, salary, joining_date, entity, employment_type
(+ conditional start/end/duration, prev_contract_date, gender, hod_name/designation, jd_doc_id, is_transition).

| emp field | Source | Confidence |
|---|---|---|
| `name` | `applications.contract_drafting_full_legal_name` ?? `candidates.first_name+last_name` | auto (prefer legal name) |
| `cnic` | `applications.contract_drafting_cnic_number` else **manual** | auto when submitted |
| `email` | `candidates.email` | auto |
| `designation` | `jobs.title` | auto |
| `department` | `jobs.department` | auto |
| `employment_type` | map `jobs.employment_type`: `Permanent`→`full_time`, `Contractual`→`project` (+ manual override to part_time) | auto + confirm |
| `entity` | **manual** (owt/opl/taleemabad/orenda — not in pipeline) | manual |
| `salary` | **manual** (`jobs.min/max_budget` nearly always null) | manual |
| `joining_date` | **manual** / from offer email | manual |
| `gender` | **manual** (drives Mr./Miss) | manual |
| `hod_name` / `hod_designation` | **manual** (hint: `jobs.hiring_manager`, `jobs.poc_person`) | manual |
| `jd_doc_id` | **manual** paste/picker. Future: feed `jobs.jd_text` directly into Annexure-A | manual (v1) |
| `is_transition` | **manual** toggle (removes probation clause) | manual |
| `remote_date`/`inperson_date` | hint from `jobs.work_type` (In-Person/Remote); dates manual | manual |

Net: **name, CNIC, designation, department, email, employment_type can be auto-prefilled**; entity,
salary, joining_date, gender, HoD, JD are manual (with Gmail-extraction as optional later suggestions).

## jobs reference values
- `jobs.employment_type`: Permanent (22), Contractual (5), None (1)
- `jobs.work_type`: In-Person (26), Remote (1), None (1)
- `jobs.department`: Program, Product, Engineering, … (free text)
- `jobs.jd_text` (text) present — candidate JD source for Annexure-A (future enhancement)

## Action items this changes in the plan
1. Replace the broken `get_candidates(status)` usage with a new `get_offer_pipeline()` querying `applications`.
2. The Form auto-prefills 6 fields from Markaz (was assumed ~3) — less manual entry than feared.
3. Add an `EMPLOYMENT_TYPE_MAP` (Permanent→full_time, Contractual→project) with manual override.
4. Still-pending Phase 0 item: confirm the service account (ayat@niete.edu.pk) can copy the 8 template
   docs + read JD docs — BLOCKED until the service token is minted (needs Google admin step).
