#!/usr/bin/env python3
"""Cross-check current Markaz sheet with previous year's insurance sheet."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

def get_markaz_data():
    """Get current Markaz employee data."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            ep.id,
            ep.employee_id,
            COALESCE(u.first_name || ' ' || u.last_name, ep.user_id) as full_name,
            u.first_name,
            u.last_name,
            ep.cnic_number,
            ep.date_of_birth,
            ep.gender,
            ep.marital_status,
            ep.father_husband_name,
            ep.job_title,
            ep.department,
            ep.payroll_entity,
            ep.contact_number,
            ep.official_email,
            ep.bank_name,
            ep.bank_account_number,
            ep.bank_account_title,
            ep.joining_date,
            ep.user_id
        FROM employee_profiles ep
        LEFT JOIN users u ON ep.user_id = u.id
        WHERE ep.compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        ORDER BY ep.employee_id, COALESCE(u.first_name || ' ' || u.last_name, ep.user_id)
    """)

    employees = cur.fetchall()
    conn.close()
    return {str(e['employee_id']): e for e in employees if e['employee_id']}

def analyze_markaz_data():
    """Analyze missing data in Markaz."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("\n" + "=" * 100)
    print("ANALYZING MARKAZ DATA - MISSING FIELDS")
    print("=" * 100 + "\n")

    # Check CNIC missing
    cur.execute("""
        SELECT COUNT(*) as count FROM employee_profiles
        WHERE compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        AND (cnic_number IS NULL OR cnic_number = '')
    """)
    result = cur.fetchone()
    missing_cnic = result['count']

    # Check DOB missing
    cur.execute("""
        SELECT COUNT(*) as count FROM employee_profiles
        WHERE compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        AND date_of_birth IS NULL
    """)
    result = cur.fetchone()
    missing_dob = result['count']

    # Check bank info missing
    cur.execute("""
        SELECT COUNT(*) as count FROM employee_profiles
        WHERE compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        AND (bank_account_number IS NULL OR bank_account_number = '')
    """)
    result = cur.fetchone()
    missing_bank = result['count']

    # Check contact missing
    cur.execute("""
        SELECT COUNT(*) as count FROM employee_profiles
        WHERE compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        AND (contact_number IS NULL OR contact_number = '')
    """)
    result = cur.fetchone()
    missing_contact = result['count']

    # Get employees with missing CNIC
    cur.execute("""
        SELECT
            employee_id,
            COALESCE(u.first_name || ' ' || u.last_name, ep.user_id) as full_name,
            job_title,
            payroll_entity
        FROM employee_profiles ep
        LEFT JOIN users u ON ep.user_id = u.id
        WHERE compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        AND (cnic_number IS NULL OR cnic_number = '')
        ORDER BY employee_id
    """)
    no_cnic = cur.fetchall()

    conn.close()

    print(f"Missing CNIC: {missing_cnic} employees")
    print(f"Missing DOB: {missing_dob} employees")
    print(f"Missing Bank Account: {missing_bank} employees")
    print(f"Missing Contact: {missing_contact} employees")

    print(f"\n\nEmployees WITHOUT CNIC ({missing_cnic}):")
    print("-" * 100)
    for emp in no_cnic:
        print(f"  ID: {emp['employee_id']:<6} | {emp['full_name']:<35} | {emp['job_title']:<40} | {emp['payroll_entity']}")

    return {
        'missing_cnic': missing_cnic,
        'missing_dob': missing_dob,
        'missing_bank': missing_bank,
        'missing_contact': missing_contact,
        'no_cnic_list': no_cnic
    }

def main():
    print("\n" + "=" * 100)
    print("CROSS-CHECK INSURANCE DATA")
    print("=" * 100)

    print("\n[Step 1] Fetching current Markaz data...")
    markaz_data = get_markaz_data()
    print(f"[OK] Fetched {len(markaz_data)} employees from Markaz")

    print("\n[Step 2] Analyzing Markaz data gaps...")
    analysis = analyze_markaz_data()

    print("\n[Step 3] Summary of data issues...")
    print("=" * 100)
    print("\nCurrent Markaz Status:")
    print(f"  - Employees with missing CNIC: {analysis['missing_cnic']}")
    print(f"  - Employees with missing DOB: {analysis['missing_dob']}")
    print(f"  - Employees with missing Bank Account: {analysis['missing_bank']}")
    print(f"  - Employees with missing Contact: {analysis['missing_contact']}")

    print("\n" + "=" * 100)
    print("NEXT STEP: User will provide previous insurance sheet for cross-check")
    print("=" * 100)

if __name__ == "__main__":
    main()
