#!/usr/bin/env python3
"""Check the 14 employees without CNIC."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)

print("\n" + "=" * 100)
print("14 EMPLOYEES WITHOUT CNIC (Haven't logged in/completed profile yet)")
print("=" * 100)

cur.execute("""
    SELECT
        id,
        employee_id,
        user_id,
        cnic_number,
        marital_status,
        date_of_birth,
        gender,
        job_title,
        department,
        payroll_entity,
        contact_number,
        official_email
    FROM employee_profiles
    WHERE compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
    AND (cnic_number IS NULL OR cnic_number = '')
    ORDER BY user_id
""")

employees = cur.fetchall()
print(f"\nFound {len(employees)} employees:\n")

for i, emp in enumerate(employees, 1):
    print(f"{i}. {emp['user_id']}")
    print(f"   Employee ID: {emp['employee_id']}")
    print(f"   Job Title: {emp['job_title'] or '[Not filled]'}")
    print(f"   Department: {emp['department'] or '[Not filled]'}")
    print(f"   Entity: {emp['payroll_entity'] or '[Not filled]'}")
    print(f"   Contact: {emp['contact_number'] or '[Not filled]'}")
    print()

conn.close()
