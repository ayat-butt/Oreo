#!/usr/bin/env python3
"""
Preview what the updated tracker sheet will look like with:
- 16 missing employees added
- Level column added
- Cleaner structure
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from collections import defaultdict
from hr_assistant.config import get_google_services

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")
SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
GID = "654305400"

def fetch_markaz_data():
    """Fetch all employees with levels."""
    conn = psycopg2.connect(DB_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT
                u.id,
                u.first_name || ' ' || u.last_name AS full_name,
                ep.level,
                ep.job_title,
                ep.department,
                ep.line_manager_id,
                (SELECT u2.first_name || ' ' || u2.last_name
                 FROM users u2 WHERE u2.id = ep.line_manager_id) AS manager_name
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL AND u.archived_at IS NULL
            ORDER BY u.first_name, u.last_name
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def read_tracker_sheet():
    """Read the current tracker sheet."""
    services = get_google_services()
    sheets = services["sheets"]

    metadata = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == GID:
            sheet_name = sheet["properties"]["title"]
            break

    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1:F200"
    ).execute()

    return result.get("values", [])

def normalize_name(name):
    """Normalize name for matching."""
    return name.lower().strip().replace("  ", " ")

def find_employee(name, markaz_employees):
    """Find employee in Markaz data."""
    name_norm = normalize_name(name)
    for emp in markaz_employees:
        if normalize_name(emp["full_name"]) == name_norm:
            return emp
    # Try partial match
    parts = name_norm.split()
    for emp in markaz_employees:
        emp_parts = normalize_name(emp["full_name"]).split()
        if any(part in emp_parts for part in parts):
            return emp
    return None

def main():
    print("="*140)
    print("PREVIEW: UPDATED TRACKER SHEET")
    print("="*140)

    print("\n[1] Loading Markaz data...")
    markaz_employees = fetch_markaz_data()
    print(f"    ✓ {len(markaz_employees)} employees loaded")

    print("\n[2] Reading current tracker sheet...")
    tracker_rows = read_tracker_sheet()
    print(f"    ✓ {len(tracker_rows)} rows read")

    print("\n[3] Planning updates...")

    # Create lookup by name
    by_name = {emp["full_name"]: emp for emp in markaz_employees}
    tracker_names = set()

    # Extract names from tracker
    for row in tracker_rows[1:]:
        for col_idx in [1, 2, 3, 4]:
            if len(row) > col_idx:
                cell = str(row[col_idx]).strip()
                if not cell or cell.startswith("#"):
                    continue
                if col_idx == 4:  # Team Members
                    for name in cell.split(","):
                        name = name.strip()
                        if name:
                            tracker_names.add(name)
                elif cell:
                    tracker_names.add(cell)

    # Find missing employees
    missing = []
    for emp in markaz_employees:
        emp_name_norm = normalize_name(emp["full_name"])
        found = False
        for tracker_name in tracker_names:
            if normalize_name(tracker_name) == emp_name_norm:
                found = True
                break
        if not found:
            missing.append(emp)

    print(f"    ✓ {len(missing)} employees missing from tracker")

    # Show missing employees with details
    print("\n" + "="*140)
    print("MISSING EMPLOYEES TO ADD:")
    print("="*140)
    print(f"\n{'#':<3} {'Name':<35} {'Level':<10} {'Manager':<35} {'Department':<25}")
    print("-"*140)

    for idx, emp in enumerate(sorted(missing, key=lambda x: x["full_name"]), 1):
        level = emp.get("level") or "—"
        mgr = emp.get("manager_name") or "—"
        dept = emp.get("department") or "—"
        print(f"{idx:<3} {emp['full_name']:<35} {level:<10} {mgr:<35} {dept:<25}")

    # Show level statistics
    print("\n" + "="*140)
    print("LEVEL DISTRIBUTION (All Employees):")
    print("="*140)

    level_counts = {}
    for emp in markaz_employees:
        level = emp.get("level") or "—"
        level_counts[level] = level_counts.get(level, 0) + 1

    for level in sorted(level_counts.keys(), key=lambda x: (x != "II-B", x)):
        count = level_counts[level]
        bar = "█" * (count // 2)
        print(f"  {level:<15} {bar} ({count})")

    # Show updated structure sample
    print("\n" + "="*140)
    print("SAMPLE OF UPDATED SHEET STRUCTURE:")
    print("="*140)
    print("\nCurrent columns:")
    print("  Department | SMT | Team Lead | Reports To | Team Member | # Members")
    print("\nNew columns:")
    print("  Department | SMT | SMT Level | Team Lead | TL Level | Reports To | Team Member | # Members")
    print("\nOr cleaner alternative (if you prefer):")
    print("  Department | Name | Level | Job Title | Manager | Direct Reports")

    # Show 5 sample rows with levels added
    print("\n" + "-"*140)
    print("SAMPLE WITH LEVELS ADDED (from current tracker):\n")

    print(f"{'Department':<30} {'Name':<30} {'Level':<10} {'Manager':<30} {'Direct Reports':<5}")
    print("-"*140)

    sample_count = 0
    for row in tracker_rows[1:]:
        if sample_count >= 5:
            break
        if len(row) > 2 and row[2]:  # Team Lead column
            name = row[2].strip()
            emp = find_employee(name, markaz_employees)
            if emp:
                level = emp.get("level") or "—"
                mgr = emp.get("manager_name") or "—"
                dept = row[0] if len(row) > 0 else "—"
                reports = row[5] if len(row) > 5 else "—"
                print(f"{dept:<30} {name:<30} {level:<10} {mgr:<30} {reports:<5}")
                sample_count += 1

    print("\n" + "="*140)
    print("ACTION PLAN:")
    print("="*140)
    print("\n✓ ADD 16 missing employees to the tracker")
    print("✓ ADD 'Level' column for each person")
    print("✓ UPDATE all level fields from Markaz")
    print("✓ Keep existing structure (Department, SMT, Team Lead, etc.)")
    print("\nProceed with update? (yes/no)")

if __name__ == "__main__":
    main()
