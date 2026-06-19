#!/usr/bin/env python3
"""Export employee profiles and dependents to CSV files."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime
import csv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

def format_date(date_obj):
    """Format date for display."""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return str(date_obj)[:10]

def export_employees_csv():
    """Export employee profiles to CSV."""
    print("Fetching employees...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            user_id,
            employee_id,
            cnic_number,
            marital_status,
            date_of_birth,
            father_husband_name,
            gender,
            job_title,
            department,
            payroll_entity,
            joining_date,
            contact_number,
            official_email,
            dependents as dependents_count
        FROM employee_profiles
        WHERE cnic_number IS NOT NULL
        ORDER BY user_id
    """)

    employees = cur.fetchall()
    conn.close()

    # Write to CSV
    output_file = "c:\\Agent Oreo\\output\\EMPLOYEES_PROFILES.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Employee Name (user_id)",
            "Employee ID",
            "CNIC",
            "Marital Status",
            "Date of Birth",
            "Father/Husband Name",
            "Gender",
            "Job Title",
            "Department",
            "Payroll Entity",
            "Joining Date",
            "Contact Number",
            "Official Email",
            "Dependents Count"
        ])

        # Data
        for emp in employees:
            writer.writerow([
                emp['user_id'] or "",
                emp['employee_id'] or "",
                emp['cnic_number'] or "",
                emp['marital_status'] or "",
                format_date(emp['date_of_birth']),
                emp['father_husband_name'] or "",
                emp['gender'] or "",
                emp['job_title'] or "",
                emp['department'] or "",
                emp['payroll_entity'] or "",
                format_date(emp['joining_date']),
                emp['contact_number'] or "",
                emp['official_email'] or "",
                emp['dependents_count'] or "0"
            ])

    print(f"[OK] Exported {len(employees)} employees to {output_file}")
    return len(employees)

def export_dependents_csv():
    """Export dependents to CSV."""
    print("Fetching dependents...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            ep.user_id,
            ep.employee_id,
            d.name as dependent_name,
            d.relationship,
            d.date_of_birth,
            d.cnic_number
        FROM dependents d
        JOIN employee_profiles ep ON d.employee_profile_id = ep.id
        ORDER BY ep.user_id, d.name
    """)

    dependents = cur.fetchall()
    conn.close()

    # Write to CSV
    output_file = "c:\\Agent Oreo\\output\\EMPLOYEE_DEPENDENTS.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Employee Name (user_id)",
            "Employee ID",
            "Dependent Name",
            "Relationship",
            "Date of Birth",
            "CNIC"
        ])

        # Data
        for dep in dependents:
            writer.writerow([
                dep['user_id'] or "",
                dep['employee_id'] or "",
                dep['dependent_name'] or "",
                dep['relationship'] or "",
                format_date(dep['date_of_birth']),
                dep['cnic_number'] or ""
            ])

    print(f"[OK] Exported {len(dependents)} dependents to {output_file}")
    return len(dependents)

def main():
    print("\n" + "=" * 80)
    print("EXPORTING EMPLOYEE PROFILES & DEPENDENTS")
    print("=" * 80)
    print()

    emp_count = export_employees_csv()
    dep_count = export_dependents_csv()

    print()
    print("=" * 80)
    print("EXPORT COMPLETE")
    print("=" * 80)
    print(f"[OK] Total Employees: {emp_count}")
    print(f"[OK] Total Dependents: {dep_count}")
    print()
    print("Files created:")
    print("  1. output/EMPLOYEES_PROFILES.csv")
    print("  2. output/EMPLOYEE_DEPENDENTS.csv")
    print()
    print("Next steps:")
    print("  • Upload these CSV files to Google Sheets")
    print("  • Or import them into Excel for further processing")

if __name__ == "__main__":
    main()
