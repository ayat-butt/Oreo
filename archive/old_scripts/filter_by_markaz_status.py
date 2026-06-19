#!/usr/bin/env python3
"""
Filter the 82 missing employees by checking Markaz for:
1. Alumni status
2. CPD Coaches / Coach roles
Remove those from the missing list.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

# The 82 truly missing employees
MISSING_EMPLOYEES = [
    "Alamgeer Abbas", "Aleeha Noor", "Ali Sipra", "Ammad Rasheed", "Aneela khaliq",
    "Arbab Abdul Khalil", "Ayat Butt", "Ayesha Raza", "Bibi Raheela", "Bushra",
    "Danish Iqbal", "Fakhr Ul Islam", "Fareeda Sanam", "Farheen Foad", "Fatima Khan",
    "Ghulam Sarwar", "Gulraiz Ghaffar", "Hamza Mehmood", "Hamza Razaq", "Hamza Siddique",
    "Hashir Hussain", "Hassan Shahzad", "Hira Naz", "Iffat Maab Akhtar", "Ifraah Javed",
    "JUNAID AHMED", "Jamshaid Ahmad", "Jarrar Ali Khan", "Javeria Khalil", "Jeremy Sigamony",
    "Khuda Bakhsh", "Komal Babar", "M. Saim", "Maheen Mirza", "Mahreen Rabi",
    "Maria Kareem", "Maryam Yousaf", "Meerab Din", "Mehreen Hussain", "Mehwish Allah Ditta",
    "Mehwish Bibi", "Minha Khan", "Moiz Khan", "Mubashar Zia", "Mubasher Irfan",
    "Muhammad Abubakr", "Muhammad Hammad Sarfraz", "Muhammad Haris", "Muhammad Muneeb", "Muhammad Umar Raza",
    "Muhammad Waqas Zubair", "Muhammad Zain ul Abadin", "Munira Shah", "NADEEM AHMAD", "Nawal Khurram",
    "Nouman Alam", "Ramisha Riaz Sheikh", "Rida Abbas", "Saaim Asif", "Saima Jabeen",
    "Saleh Muhammad", "Salman Sohail", "Sana Ishtiaq", "Shareen Umer", "Shazmina Sharif",
    "Shiza Kamil", "Shoaib ud Din", "Sohaib Danish", "Sohail Anjum", "Syed Zaamin Abbas",
    "Syeda Mariam Naqvi", "Syeda Mehwish Ali", "Tajdar Shakeel", "Tehniat Taqdees", "Tehreem batool",
    "Toseef Ur Rehman", "Wajiha Malik", "Waleed Abdullah", "Zainab Fatima", "Zainab Zaheer",
    "Zara Bibi", "Zarmeen Kausar"
]

def normalize_name(name):
    """Normalize name."""
    return name.lower().strip().replace("  ", " ")

def fetch_from_markaz():
    """Fetch alumni and Coach roles from Markaz."""
    conn = psycopg2.connect(DB_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get alumni (archived users)
        print("[Querying Markaz for alumni and coaches...]")

        cur.execute("""
            SELECT
                u.id,
                u.first_name || ' ' || u.last_name AS full_name,
                ep.job_title,
                u.archived_at,
                u.deleted_at,
                u.status
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.archived_at IS NOT NULL
               OR u.deleted_at IS NOT NULL
               OR LOWER(ep.job_title) LIKE '%coach%'
               OR LOWER(ep.job_title) LIKE '%cpd%'
            ORDER BY u.first_name, u.last_name
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def main():
    print("="*120)
    print("FILTERING MISSING EMPLOYEES BY MARKAZ STATUS")
    print("="*120)

    print("\n[1] Fetching from Markaz (alumni + coaches)...")
    try:
        markaz_data = fetch_from_markaz()
        print(f"    ✓ Found {len(markaz_data)} entries (alumni + coaches)")
    except Exception as e:
        print(f"    ✗ Error connecting to Markaz: {e}")
        print(f"    Proceeding with available data...")
        markaz_data = []

    # Categorize the Markaz entries
    alumni = []
    coaches = []

    for emp in markaz_data:
        name = emp["full_name"]
        job_title = emp.get("job_title") or "—"
        archived = emp.get("archived_at")
        deleted = emp.get("deleted_at")

        if archived or deleted:
            alumni.append((name, job_title))

        if job_title and ("coach" in job_title.lower() or "cpd" in job_title.lower()):
            coaches.append((name, job_title))

    print(f"    ✓ Alumni (archived/deleted): {len(alumni)}")
    print(f"    ✓ CPD Coaches/Coach roles: {len(coaches)}")

    # Cross-check with missing employees
    print("\n[2] Cross-checking with 82 missing employees...")

    to_remove_alumni = []
    to_remove_coaches = []
    still_missing = []

    for missing_name in MISSING_EMPLOYEES:
        missing_norm = normalize_name(missing_name)
        found_as_alumni = False
        found_as_coach = False

        # Check alumni
        for alumni_name, _ in alumni:
            if normalize_name(alumni_name) == missing_norm:
                to_remove_alumni.append((missing_name, alumni_name))
                found_as_alumni = True
                break

        # Check coaches
        if not found_as_alumni:
            for coach_name, job_title in coaches:
                if normalize_name(coach_name) == missing_norm:
                    to_remove_coaches.append((missing_name, coach_name, job_title))
                    found_as_coach = True
                    break

        # If not found in either, they're still missing
        if not found_as_alumni and not found_as_coach:
            still_missing.append(missing_name)

    print(f"    ✓ {len(to_remove_alumni)} to remove (alumni)")
    print(f"    ✓ {len(to_remove_coaches)} to remove (coaches)")
    print(f"    ✓ {len(still_missing)} TRULY MISSING")

    # Report
    if to_remove_alumni:
        print("\n" + "="*120)
        print(f"TO REMOVE - ALUMNI/ARCHIVED ({len(to_remove_alumni)}):")
        print("="*120)
        for missing, actual in sorted(to_remove_alumni):
            print(f"  • {missing}")

    if to_remove_coaches:
        print("\n" + "="*120)
        print(f"TO REMOVE - CPD COACHES/COACHES ({len(to_remove_coaches)}):")
        print("="*120)
        for missing, actual, title in sorted(to_remove_coaches):
            print(f"  • {missing:<40} (Role: {title})")

    if still_missing:
        print("\n" + "="*120)
        print(f"FINAL TRULY MISSING EMPLOYEES ({len(still_missing)}):")
        print("="*120)
        print(f"\nTotal: {len(still_missing)}\n")
        for name in sorted(still_missing):
            print(f"  • {name}")

    print("\n" + "="*120)
    print("FINAL SUMMARY:")
    print("="*120)
    print(f"\nStarting with: 82 truly missing")
    print(f"  - Remove alumni: {len(to_remove_alumni)}")
    print(f"  - Remove coaches: {len(to_remove_coaches)}")
    print(f"  = FINAL missing: {len(still_missing)}")

if __name__ == "__main__":
    main()
