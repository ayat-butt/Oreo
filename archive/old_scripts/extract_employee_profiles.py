#!/usr/bin/env python3
"""Extract employee profiles and dependents from Markaz EMPLOYEE MANAGEMENT section."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

def get_employee_profiles():
    """Fetch all employee profiles from Markaz."""
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # First, let's check what columns are available
        print("=" * 80)
        print("CHECKING AVAILABLE COLUMNS IN EMPLOYEE_PROFILES TABLE")
        print("=" * 80)

        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'employee_profiles'
            ORDER BY ordinal_position
        """)

        columns = cur.fetchall()
        print("\nAvailable columns:")
        for col in columns:
            print(f"  - {col['column_name']} ({col['data_type']})")

        # Now fetch employee profile data
        print("\n" + "=" * 80)
        print("FETCHING EMPLOYEE PROFILE DATA")
        print("=" * 80)

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
                official_email
            FROM employee_profiles
            WHERE cnic_number IS NOT NULL
            ORDER BY user_id
        """)

        employees = cur.fetchall()
        print(f"\nFound {len(employees)} employees with profile data")

        if employees:
            print("\nSample employee record (first record):")
            first = employees[0]
            for key, value in first.items():
                print(f"  {key}: {value}")

        conn.close()
        return employees

    except Exception as e:
        print(f"Error connecting to Markaz: {e}")
        return []

def get_dependents():
    """Fetch all dependents from Markaz."""
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check columns in dependents table
        print("\n" + "=" * 80)
        print("CHECKING AVAILABLE COLUMNS IN DEPENDENTS TABLE")
        print("=" * 80)

        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'dependents'
            ORDER BY ordinal_position
        """)

        columns = cur.fetchall()
        if columns:
            print("\nAvailable columns in dependents table:")
            for col in columns:
                print(f"  - {col['column_name']} ({col['data_type']})")
        else:
            print("\nNo 'dependents' table found. Checking for alternative table names...")

            # Try to find related tables
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND (table_name LIKE '%dependent%' OR table_name LIKE '%family%' OR table_name LIKE '%profile%')
                ORDER BY table_name
            """)

            tables = cur.fetchall()
            print("\nFound related tables:")
            for table in tables:
                print(f"  - {table['table_name']}")

        # Try to fetch dependents with employee info
        try:
            cur.execute("""
                SELECT
                    d.id,
                    d.employee_profile_id,
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
            print(f"\nFound {len(dependents)} dependent records")

            if dependents:
                print("\nSample dependent record (first record):")
                first = dependents[0]
                for key, value in first.items():
                    print(f"  {key}: {value}")

            conn.close()
            return dependents

        except psycopg2.Error as e:
            print(f"\nCould not query 'dependents' table directly: {e}")
            conn.close()
            return []

    except Exception as e:
        print(f"Error fetching dependents: {e}")
        return []

def main():
    print("\n" + "=" * 80)
    print("MARKAZ EMPLOYEE PROFILE & DEPENDENTS DATA EXTRACTION")
    print("=" * 80)

    employees = get_employee_profiles()
    dependents = get_dependents()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Employees: {len(employees)}")
    print(f"Total Dependents: {len(dependents)}")

    # Save raw data for reference
    if employees or dependents:
        output = {
            "extraction_date": datetime.now().isoformat(),
            "employees_count": len(employees),
            "dependents_count": len(dependents),
            "employees": [dict(e) if hasattr(e, 'items') else e for e in employees],
            "dependents": [dict(d) if hasattr(d, 'items') else d for d in dependents]
        }

        with open("c:\\Agent Oreo\\markaz_extraction.json", "w") as f:
            json.dump(output, f, indent=2, default=str)

        print("\nData saved to: markaz_extraction.json")

if __name__ == "__main__":
    main()
