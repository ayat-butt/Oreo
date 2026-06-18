"""Phase 0c — READ-ONLY: confirm the offer->contract field mapping.

For applications at the offer/hired stage, determine how much contract data Markaz
already holds vs what must be entered manually. PII (CNIC) is MASKED — we report
presence/absence, not values. STRICTLY READ-ONLY.
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")


def main():
    conn = psycopg2.connect(DB_URL)
    conn.set_session(readonly=True, autocommit=True)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    print("=" * 78)
    print("PHASE 0c — OFFER -> CONTRACT MAPPING (read-only, CNIC masked)")
    print("=" * 78)

    # 1) jobs.employment_type / work_type / type distinct values -> map to engine
    print("\n[1] jobs.employment_type distinct")
    cur.execute("SELECT employment_type AS v, COUNT(*) n FROM jobs GROUP BY employment_type ORDER BY n DESC")
    for r in cur.fetchall():
        print(f"    {str(r['v']):30} {r['n']}")
    print("\n[1b] jobs.work_type distinct")
    cur.execute("SELECT work_type AS v, COUNT(*) n FROM jobs GROUP BY work_type ORDER BY n DESC")
    for r in cur.fetchall():
        print(f"    {str(r['v']):30} {r['n']}")
    print("\n[1c] jobs.type distinct")
    cur.execute("SELECT type AS v, COUNT(*) n FROM jobs GROUP BY type ORDER BY n DESC")
    for r in cur.fetchall():
        print(f"    {str(r['v']):30} {r['n']}")

    # 2) For offer/hired applications: how populated are the contract fields?
    print("\n[2] applications at status in (offer, hired): contract-data completeness")
    cur.execute("""
        SELECT
          COUNT(*) AS total,
          COUNT(contract_drafting_full_legal_name) AS has_legal_name,
          COUNT(contract_drafting_cnic_number)      AS has_cnic,
          COUNT(contract_drafting_submitted_at)     AS has_submitted_at
        FROM applications
        WHERE status IN ('offer','hired')
    """)
    print(f"    {dict(cur.fetchone())}")

    # 3) sample offer/hired rows joined to candidate + job (CNIC masked)
    print("\n[3] sample offer/hired rows (CNIC masked, joined to candidate+job)")
    cur.execute("""
        SELECT a.id AS app_id, a.status, a.stage,
               c.first_name, c.last_name, c.email,
               a.contract_drafting_full_legal_name AS legal_name,
               a.contract_drafting_cnic_number AS cnic,
               a.contract_drafting_submitted_at AS contract_submitted,
               j.title AS job_title, j.department AS job_dept,
               j.employment_type, j.work_type, j.min_budget, j.max_budget, j.currency
        FROM applications a
        LEFT JOIN candidates c ON a.candidate_id = c.id
        LEFT JOIN jobs j ON a.job_id = j.id
        WHERE a.status IN ('offer','hired')
        ORDER BY a.updated_at DESC NULLS LAST
        LIMIT 8
    """)
    for r in cur.fetchall():
        cnic = r["cnic"]
        cnic_mask = (cnic[:3] + "****" + cnic[-2:]) if cnic else "—(none)"
        print(f"    app#{r['app_id']} [{r['status']}/{r['stage']}] "
              f"{r['first_name']} {r['last_name']} <{r['email']}>")
        print(f"        legal_name={r['legal_name'] or '—'} | cnic={cnic_mask} "
              f"| contract_submitted={'yes' if r['contract_submitted'] else 'no'}")
        print(f"        job={r['job_title']} / dept={r['job_dept']} / emp_type={r['employment_type']} "
              f"/ work={r['work_type']} / budget={r['min_budget']}-{r['max_budget']} {r['currency']}")

    # 4) status_transitions: does it record an 'offer_accepted'-like event?
    print("\n[4] status_transitions table")
    cur.execute("""SELECT column_name, data_type FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='status_transitions' ORDER BY ordinal_position""")
    cols = cur.fetchall()
    if cols:
        for c in cols:
            print(f"    {c['column_name']:30} {c['data_type']}")
        # distinct to_status if present
        names = {c["column_name"] for c in cols}
        for col in ("to_status", "new_status", "status", "to_stage"):
            if col in names:
                cur.execute(f"SELECT {col} AS v, COUNT(*) n FROM status_transitions GROUP BY {col} ORDER BY n DESC LIMIT 30")
                print(f"    >>> DISTINCT {col}:")
                for r in cur.fetchall():
                    print(f"          {str(r['v']):30} {r['n']}")
    else:
        print("    (no such table)")

    cur.close()
    conn.close()
    print("\nDONE (read-only).")


if __name__ == "__main__":
    main()
