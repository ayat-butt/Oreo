#!/usr/bin/env python3
"""Check if the 14 employees have any dependents."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)

print("\nChecking dependents for the 14 employees without CNIC:\n")

# Check if these 14 employees have dependents
cur.execute("""
    SELECT
        ep.user_id,
        ep.employee_id,
        COUNT(d.id) as dependent_count
    FROM employee_profiles ep
    LEFT JOIN dependents d ON ep.id = d.employee_profile_id
    WHERE ep.compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
    AND (ep.cnic_number IS NULL OR ep.cnic_number = '')
    GROUP BY ep.id, ep.user_id, ep.employee_id
    ORDER BY dependent_count DESC
""")

results = cur.fetchall()
total_deps = sum(r['dependent_count'] for r in results)

for row in results:
    status = f"{row['dependent_count']} dependent(s)" if row['dependent_count'] > 0 else "No dependents"
    emp_id = row['employee_id'] if row['employee_id'] else "None"
    print(f"  {emp_id:>4} - {status}")

print(f"\nTotal dependents for these 14 employees: {total_deps}")

conn.close()
