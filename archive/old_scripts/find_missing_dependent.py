#!/usr/bin/env python3
"""Find the missing dependent(s)."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import csv
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

def get_all_dependents():
    """Get ALL dependents from database."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            d.id,
            d.employee_profile_id,
            ep.user_id,
            ep.employee_id,
            d.name as dependent_name,
            d.relationship,
            d.date_of_birth,
            d.cnic_number,
            ep.compensation_status
        FROM dependents d
        JOIN employee_profiles ep ON d.employee_profile_id = ep.id
        WHERE ep.compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        ORDER BY ep.user_id, d.name
    """)

    dependents = cur.fetchall()
    conn.close()
    return dependents

def get_dependents_from_csv():
    """Get dependents from CSV file."""
    csv_deps = set()
    with open('c:/Agent Oreo/output/EMPLOYEE_DEPENDENTS.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create a unique key for each dependent
            key = (row['Employee ID'], row['Dependent Name'], row['CNIC'])
            csv_deps.add(key)
    return csv_deps

def main():
    print("\n" + "=" * 100)
    print("FINDING MISSING DEPENDENT(S)")
    print("=" * 100 + "\n")

    print("Fetching all dependents from database...")
    db_deps = get_all_dependents()
    print(f"[OK] Found {len(db_deps)} dependents in database\n")

    print("Fetching dependents from CSV file...")
    csv_deps = get_dependents_from_csv()
    print(f"[OK] Found {len(csv_deps)} dependents in CSV\n")

    print("Comparing...")

    # Create set of DB dependents
    db_set = set()
    for dep in db_deps:
        key = (str(dep['employee_id']), dep['dependent_name'], dep['cnic_number'] or "")
        db_set.add(key)

    # Find missing
    missing = db_set - csv_deps
    extra = csv_deps - db_set

    if missing:
        print(f"\n[FOUND] {len(missing)} dependent(s) MISSING from CSV/Sheet:\n")
        for emp_id, dep_name, cnic in sorted(missing):
            print(f"  Employee ID: {emp_id}")
            print(f"  Dependent Name: {dep_name}")
            print(f"  CNIC: {cnic}")
            # Find full details
            for dep in db_deps:
                if dep['employee_id'] == emp_id and dep['dependent_name'] == dep_name:
                    print(f"  Relationship: {dep['relationship']}")
                    print(f"  DOB: {dep['date_of_birth']}")
                    print(f"  Employee: {dep['user_id']}")
                    print()

    if extra:
        print(f"\n[WARNING] {len(extra)} dependent(s) in CSV but NOT in database:")
        for emp_id, dep_name, cnic in sorted(extra):
            print(f"  {emp_id} - {dep_name} ({cnic})")

    if not missing and not extra:
        print("[OK] All dependents match between database and CSV!")

if __name__ == "__main__":
    main()
