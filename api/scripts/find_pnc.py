"""Read-only: find P&C (People & Culture / HR) department members + their Taleemabad emails."""
import os, psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv("MARKAZ_DB_URL")); conn.set_session(readonly=True, autocommit=True)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

print("=== distinct departments (active employees) ===")
cur.execute("""
    SELECT ep.department, COUNT(*) n
    FROM users u JOIN employee_profiles ep ON u.id = ep.user_id
    WHERE u.deleted_at IS NULL AND u.archived_at IS NULL
    GROUP BY ep.department ORDER BY ep.department
""")
for r in cur.fetchall():
    print(f"  {r['department']!r}: {r['n']}")

print("\n=== P&C / People / Culture / HR members ===")
cur.execute("""
    SELECT u.first_name, u.last_name, u.email, ep.official_email, ep.department, u.job_title
    FROM users u JOIN employee_profiles ep ON u.id = ep.user_id
    WHERE u.deleted_at IS NULL AND u.archived_at IS NULL
      AND (
        LOWER(ep.department) LIKE '%culture%' OR LOWER(ep.department) LIKE '%people%'
        OR LOWER(ep.department) LIKE '%human%'  OR LOWER(ep.department) LIKE '%p&c%'
        OR LOWER(ep.department) = 'hr' OR LOWER(ep.department) LIKE 'hr %'
        OR LOWER(ep.department) LIKE '%talent%'
      )
    ORDER BY u.first_name
""")
rows = cur.fetchall()
emails = []
for r in rows:
    email = (r["email"] or r["official_email"] or "").strip()
    print(f"  {r['first_name']} {r['last_name']:18} | {r['department']:22} | {r['job_title']} | {email} | official={r['official_email']}")
    if email:
        emails.append(email)

tal = sorted({e.lower() for e in emails if e.lower().endswith('@taleemabad.com')})
print("\n=== Taleemabad-domain P&C emails (allowlist candidates) ===")
print(",".join(tal))
cur.close(); conn.close()
