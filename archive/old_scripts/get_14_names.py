#!/usr/bin/env python3
"""Get the 14 employees with real names."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)

print("\n" + "=" * 120)
print("14 EMPLOYEES WITHOUT CNIC - REAL NAMES FROM MARKAZ")
print("=" * 120 + "\n")

cur.execute("""
    SELECT
        ep.employee_id,
        u.first_name,
        u.last_name,
        COALESCE(u.first_name || ' ' || u.last_name, ep.user_id) as full_name,
        ep.job_title,
        ep.department,
        ep.payroll_entity,
        ep.contact_number,
        ep.official_email
    FROM employee_profiles ep
    LEFT JOIN users u ON ep.user_id = u.id
    WHERE ep.compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
    AND (ep.cnic_number IS NULL OR ep.cnic_number = '')
    ORDER BY ep.payroll_entity, u.first_name, u.last_name
""")

results = cur.fetchall()

for i, emp in enumerate(results, 1):
    emp_id = emp['employee_id'] if emp['employee_id'] else "TBD"
    print(f"{i:2}. {emp['full_name']:<35} | ID: {emp_id:<6} | {emp['payroll_entity']:<20} | {emp['department']:<30}")
    if emp['job_title']:
        print(f"    Job: {emp['job_title']}")
    if emp['contact_number']:
        print(f"    Contact: {emp['contact_number']}")
    print()

conn.close()
