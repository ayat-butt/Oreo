"""Phase 0b — READ-ONLY: find where the hiring PIPELINE / OFFER / ACCEPTED stage lives.

The 'candidates' table is a raw applicant pool with no status. Find the table(s) that
track applications -> stages -> offer -> accepted, and any link candidate<->job.
STRICTLY READ-ONLY.
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

KEYWORDS = ("applic", "offer", "stage", "pipeline", "hir", "interview", "candidate", "recruit", "onboard")


def main():
    conn = psycopg2.connect(DB_URL)
    conn.set_session(readonly=True, autocommit=True)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    print("=" * 78)
    print("PHASE 0b — PIPELINE / OFFER DISCOVERY (read-only)")
    print("=" * 78)

    # all public tables
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema='public' ORDER BY table_name
    """)
    tables = [r["table_name"] for r in cur.fetchall()]
    print(f"\n[ALL TABLES] ({len(tables)})")
    for t in tables:
        print(f"  - {t}")

    # tables whose name suggests recruitment pipeline
    candidates_of_interest = [t for t in tables if any(k in t.lower() for k in KEYWORDS)]
    print(f"\n[PIPELINE-RELATED TABLES] {candidates_of_interest}")

    for t in candidates_of_interest:
        cur.execute("""
            SELECT column_name, data_type FROM information_schema.columns
            WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position
        """, (t,))
        cols = cur.fetchall()
        cur.execute(f"SELECT COUNT(*) AS n FROM {t}")
        n = cur.fetchone()["n"]
        print(f"\n--- {t}  ({n} rows) ---")
        for c in cols:
            print(f"    {c['column_name']:30} {c['data_type']}")
        # if it has a status/stage column, show distinct values
        names = {c["column_name"] for c in cols}
        for stagecol in ("status", "stage", "current_stage", "state", "pipeline_stage", "application_status"):
            if stagecol in names:
                cur.execute(f"SELECT {stagecol} AS v, COUNT(*) AS n FROM {t} GROUP BY {stagecol} ORDER BY n DESC LIMIT 40")
                print(f"    >>> DISTINCT {stagecol}:")
                for r in cur.fetchall():
                    print(f"          {str(r['v']):35} {r['n']}")

    cur.close()
    conn.close()
    print("\nDONE (read-only).")


if __name__ == "__main__":
    main()
