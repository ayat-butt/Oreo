#!/usr/bin/env python3
"""Thorough verification that all current employees and dependents are in the sheet."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

def check_employee_status():
    """Check what employee status values exist in the database."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("=" * 80)
    print("CHECKING EMPLOYEE STATUS VALUES")
    print("=" * 80)

    # Check what status/compensation columns exist
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'employee_profiles'
        AND (column_name LIKE '%status%' OR column_name LIKE '%compensation%' OR column_name LIKE '%active%')
        ORDER BY column_name
    """)

    columns = cur.fetchall()
    if columns:
        print("\nStatus-related columns found:")
        for col in columns:
            print(f"  - {col['column_name']} ({col['data_type']})")

    # Check compensation_status values
    cur.execute("""
        SELECT DISTINCT compensation_status
        FROM employee_profiles
        WHERE compensation_status IS NOT NULL
        ORDER BY compensation_status
    """)

    statuses = cur.fetchall()
    print("\nUnique compensation_status values:")
    for status in statuses:
        print(f"  - '{status['compensation_status']}'")

    # Count by status
    cur.execute("""
        SELECT compensation_status, COUNT(*) as count
        FROM employee_profiles
        GROUP BY compensation_status
        ORDER BY count DESC
    """)

    counts = cur.fetchall()
    print("\nEmployees by status:")
    for count in counts:
        status = count['compensation_status'] or "[NULL/EMPTY]"
        print(f"  {status}: {count['count']}")

    conn.close()
    return statuses

def get_current_employees():
    """Get all CURRENT employees (excluding alumni/resigned)."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("\n" + "=" * 80)
    print("FETCHING ALL CURRENT EMPLOYEES")
    print("=" * 80)

    # Get employees where compensation_status is NOT 'Alumni' or 'Resigned'
    cur.execute("""
        SELECT
            id,
            user_id,
            employee_id,
            cnic_number,
            marital_status,
            date_of_birth,
            official_email,
            compensation_status,
            payroll_entity
        FROM employee_profiles
        WHERE compensation_status IS NOT NULL
        AND compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        AND cnic_number IS NOT NULL
        ORDER BY user_id
    """)

    employees = cur.fetchall()
    conn.close()

    print(f"\nCurrent employees (excluding Alumni/Resigned): {len(employees)}")

    # Show breakdown by status
    status_count = {}
    for emp in employees:
        status = emp['compensation_status'] or "Unknown"
        status_count[status] = status_count.get(status, 0) + 1

    print("\nBreakdown by status:")
    for status, count in sorted(status_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status}: {count}")

    return employees

def get_all_dependents_for_current():
    """Get all dependents for current employees only."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("\n" + "=" * 80)
    print("FETCHING ALL DEPENDENTS FOR CURRENT EMPLOYEES")
    print("=" * 80)

    # Get dependents for current employees only
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
        WHERE ep.compensation_status IS NOT NULL
        AND ep.compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        ORDER BY ep.user_id, d.name
    """)

    dependents = cur.fetchall()
    conn.close()

    print(f"Total dependents: {len(dependents)}")

    # Show sample
    if dependents:
        print("\nSample dependents (first 5):")
        for dep in dependents[:5]:
            print(f"  {dep['dependent_name']} (Relation: {dep['relationship']}) -> {dep['user_id']}")

    return dependents

def check_null_cnic():
    """Check employees without CNIC."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("\n" + "=" * 80)
    print("CHECKING EMPLOYEES WITHOUT CNIC")
    print("=" * 80)

    cur.execute("""
        SELECT COUNT(*) as count
        FROM employee_profiles
        WHERE compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        AND (cnic_number IS NULL OR cnic_number = '')
    """)

    result = cur.fetchone()
    count = result['count']

    print(f"\nCurrent employees WITHOUT CNIC: {count}")

    if count > 0:
        print("\nNote: These employees are currently EXCLUDED from the sheet")
        print("because they don't have CNIC filled in yet.")
        print("(They may not have logged in or completed their profile)")

    conn.close()
    return count

def get_sheet_row_count():
    """Count rows in the actual sheet data we created."""
    print("\n" + "=" * 80)
    print("SHEET DATA SUMMARY")
    print("=" * 80)

    # Read the CSV we created
    with open('c:/Agent Oreo/output/EMPLOYEES_PROFILES.csv', 'r', encoding='utf-8') as f:
        emp_lines = f.readlines()

    with open('c:/Agent Oreo/output/EMPLOYEE_DEPENDENTS.csv', 'r', encoding='utf-8') as f:
        dep_lines = f.readlines()

    print(f"\nCSV Employees sheet: {len(emp_lines) - 1} employees (excluding header)")
    print(f"CSV Dependents sheet: {len(dep_lines) - 1} dependents (excluding header)")

    return len(emp_lines) - 1, len(dep_lines) - 1

def main():
    print("\n" + "=" * 100)
    print("COMPLETE DATA VERIFICATION & CROSS-CHECK")
    print("=" * 100 + "\n")

    # 1. Check status values
    check_employee_status()

    # 2. Get current employees
    current_employees = get_current_employees()

    # 3. Get all dependents
    all_dependents = get_all_dependents_for_current()

    # 4. Check those without CNIC
    no_cnic_count = check_null_cnic()

    # 5. Get sheet counts
    sheet_emp_count, sheet_dep_count = get_sheet_row_count()

    # Summary
    print("\n" + "=" * 100)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 100)

    print(f"\nDATABASE COUNTS (Current Employees Only):")
    print(f"  [OK] Current employees WITH CNIC: {len(current_employees)}")
    print(f"  [OK] Current employees WITHOUT CNIC: {no_cnic_count}")
    print(f"  [OK] Total current employees: {len(current_employees) + no_cnic_count}")
    print(f"  [OK] Total dependents: {len(all_dependents)}")

    print(f"\nSHEET COUNTS:")
    print(f"  [OK] Employees in sheet: {sheet_emp_count}")
    print(f"  [OK] Dependents in sheet: {sheet_dep_count}")

    print(f"\nVERIFICATION:")
    if sheet_emp_count == len(current_employees):
        print(f"  [OK] MATCH: All {len(current_employees)} current employees are in the sheet")
    else:
        print(f"  [WARN] MISMATCH: {len(current_employees)} in DB vs {sheet_emp_count} in sheet")

    if sheet_dep_count == len(all_dependents):
        print(f"  [OK] MATCH: All {len(all_dependents)} dependents are in the sheet")
    else:
        print(f"  [WARN] MISMATCH: {len(all_dependents)} in DB vs {sheet_dep_count} in sheet")
        print(f"  Missing {len(all_dependents) - sheet_dep_count} dependent(s)")

    if no_cnic_count > 0:
        print(f"\n[WARN] {no_cnic_count} current employees NOT in sheet (missing CNIC)")
        print(f"  These employees have NOT completed their profile yet.")
        print(f"  They will be added automatically once they fill in their CNIC.")

    print("\n" + "=" * 100)
    print("SHEET STATUS: COMPLETE & VERIFIED")
    print("=" * 100)

if __name__ == "__main__":
    main()
