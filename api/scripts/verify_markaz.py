"""Phase 0 — READ-ONLY Markaz verification.

Pins down the unknowns the whole web app depends on:
  1. candidates table columns
  2. DISTINCT candidates.status values (+ counts) -> the real "offer accepted" literal
  3. jobs table columns + how candidates link to a job/department
  4. which of the 8 engine-required contract fields exist on a candidate
     (name, cnic, designation, department, salary, joining_date, entity, employment_type)

STRICTLY READ-ONLY. Opens the connection in READ ONLY transaction mode as a hard guard.
No INSERT/UPDATE/DELETE anywhere. Safe to run against the live Markaz DB.
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

ENGINE_FIELDS = [
    "name", "cnic", "designation", "department",
    "salary", "joining_date", "entity", "employment_type",
]


def cols(cur, table):
    cur.execute(
        """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        """,
        (table,),
    )
    return cur.fetchall()


def table_exists(cur, table):
    cur.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
        (table,),
    )
    return cur.fetchone() is not None


def main():
    if not DB_URL:
        print("ERROR: MARKAZ_DB_URL not set in .env")
        return

    conn = psycopg2.connect(DB_URL)
    conn.set_session(readonly=True, autocommit=True)  # hard read-only guard
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    print("=" * 78)
    print("PHASE 0 — MARKAZ READ-ONLY VERIFICATION")
    print("=" * 78)

    # --- candidates table ---
    print("\n[1] candidates table")
    if not table_exists(cur, "candidates"):
        print("  !! no 'candidates' table found")
    else:
        cand_cols = cols(cur, "candidates")
        for c in cand_cols:
            print(f"  - {c['column_name']:30} {c['data_type']:20} null={c['is_nullable']}")
        col_names = {c["column_name"] for c in cand_cols}

        cur.execute("SELECT COUNT(*) AS n FROM candidates")
        print(f"  total rows: {cur.fetchone()['n']}")

        # [2] distinct status values
        print("\n[2] DISTINCT candidates.status (+ counts)")
        if "status" in col_names:
            cur.execute(
                "SELECT status, COUNT(*) AS n FROM candidates GROUP BY status ORDER BY n DESC"
            )
            for r in cur.fetchall():
                print(f"  - {str(r['status']):30} {r['n']}")
        else:
            print("  !! candidates has no 'status' column")

        # [4] which engine fields exist on candidate
        print("\n[4] engine-required fields present on candidates?")
        for f in ENGINE_FIELDS:
            present = [cn for cn in col_names if f.split('_')[0] in cn.lower()]
            mark = "OK " if present else "-- "
            print(f"  {mark}{f:18} -> candidate cols: {present or 'MANUAL (not in candidates)'}")

        # sample one row (structure only) — first/last/email + any status
        print("\n[sample] one candidate row (keys + truncated values)")
        cur.execute("SELECT * FROM candidates ORDER BY created_at DESC NULLS LAST LIMIT 1")
        row = cur.fetchone()
        if row:
            for k, v in row.items():
                sv = str(v)
                if len(sv) > 50:
                    sv = sv[:50] + "..."
                print(f"  {k:30} = {sv}")

    # --- jobs table ---
    print("\n[3] jobs table")
    if table_exists(cur, "jobs"):
        for c in cols(cur, "jobs"):
            print(f"  - {c['column_name']:30} {c['data_type']}")
    else:
        print("  !! no 'jobs' table")

    # --- linkage: any FK-ish columns between candidates and jobs/departments ---
    print("\n[5] linkage columns (candidate -> job / department)")
    if table_exists(cur, "candidates"):
        link = [c["column_name"] for c in cols(cur, "candidates")
                if any(k in c["column_name"].lower() for k in ("job", "depart", "role", "position", "title", "applic"))]
        print(f"  candidate link/role cols: {link or 'none obvious'}")

    cur.close()
    conn.close()
    print("\nDONE (read-only).")


if __name__ == "__main__":
    main()
