#!/usr/bin/env python3
"""
Reorganize the hierarchy sheet:
1. Audit for missing employees/team leads
2. Create a clean hierarchical structure with levels
3. Make it easy to understand who manages whom
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
    """Fetch all employees with levels and manager relationships."""
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

def extract_names_from_tracker(tracker_rows):
    """Extract all unique names mentioned in tracker sheet."""
    tracker_names = set()

    for row in tracker_rows[1:]:  # Skip header
        for col_idx in [1, 2, 3, 4]:  # SMT, Team Lead, Reports To, Team Members
            if len(row) > col_idx:
                cell = str(row[col_idx]).strip()
                if not cell or cell.startswith("#"):
                    continue

                # If it's Team Members (col 4), split by comma
                if col_idx == 4 and cell:
                    for name in cell.split(","):
                        name = name.strip()
                        if name:
                            tracker_names.add(name)
                elif cell and col_idx < 4:
                    tracker_names.add(cell)

    return tracker_names

def normalize_name(name):
    """Normalize name for matching."""
    return name.lower().strip().replace("  ", " ")

def find_employee_in_markaz(name, markaz_employees):
    """Try to find employee in Markaz (with fuzzy matching)."""
    name_norm = normalize_name(name)

    # Exact match
    for emp in markaz_employees:
        if normalize_name(emp["full_name"]) == name_norm:
            return emp

    # Partial match (last name + first part of first name)
    parts = name_norm.split()
    if len(parts) >= 2:
        for emp in markaz_employees:
            emp_parts = normalize_name(emp["full_name"]).split()
            # Check if any name part matches
            if any(part in emp_parts for part in parts):
                return emp

    return None

def build_hierarchy(markaz_employees):
    """Build manager->subordinates hierarchy from Markaz data."""
    by_id = {emp["id"]: emp for emp in markaz_employees if emp["id"]}
    by_name = {emp["full_name"]: emp for emp in markaz_employees}

    # Map manager_id to subordinates
    manages = defaultdict(list)
    for emp in markaz_employees:
        mgr_id = emp.get("line_manager_id")
        if mgr_id and mgr_id in by_id:
            manages[mgr_id].append(emp)

    return by_id, by_name, manages

def main():
    print("="*120)
    print("HIERARCHY AUDIT & REORGANIZATION")
    print("="*120)

    # Step 1: Fetch data
    print("\n[1] Fetching Markaz data...")
    markaz_employees = fetch_markaz_data()
    print(f"    ✓ {len(markaz_employees)} employees in Markaz")

    print("\n[2] Reading tracker sheet...")
    tracker_rows = read_tracker_sheet()
    print(f"    ✓ {len(tracker_rows)} rows in tracker sheet")

    # Step 2: Extract names from tracker
    print("\n[3] Extracting names from tracker sheet...")
    tracker_names = extract_names_from_tracker(tracker_rows)
    print(f"    ✓ {len(tracker_names)} unique names in tracker")

    # Step 3: Cross-check
    print("\n[4] Cross-checking tracker names with Markaz...")
    by_id, by_name, manages = build_hierarchy(markaz_employees)

    found = []
    missing = []

    for name in sorted(tracker_names):
        emp = find_employee_in_markaz(name, markaz_employees)
        if emp:
            found.append((name, emp))
        else:
            missing.append(name)

    print(f"    ✓ {len(found)} names found in Markaz")
    print(f"    ⚠ {len(missing)} names NOT found in Markaz")

    if missing:
        print("\n    Missing employees from Markaz:")
        for name in sorted(missing):
            print(f"      - {name}")

    # Step 4: Check for employees in Markaz NOT in tracker
    print("\n[5] Checking for employees in Markaz but NOT in tracker...")
    tracker_names_lower = {normalize_name(n) for n in tracker_names}
    not_in_tracker = []

    for emp in markaz_employees:
        emp_name_lower = normalize_name(emp["full_name"])
        if emp_name_lower not in tracker_names_lower:
            not_in_tracker.append(emp)

    print(f"    ⚠ {len(not_in_tracker)} employees in Markaz but NOT in tracker")

    if not_in_tracker:
        print("\n    Employees missing from tracker:")
        for emp in sorted(not_in_tracker, key=lambda x: x["full_name"])[:15]:
            level = emp.get("level") or "—"
            mgr = emp.get("manager_name") or "—"
            print(f"      - {emp['full_name']:<35} | Level: {level:<10} | Manager: {mgr}")
        if len(not_in_tracker) > 15:
            print(f"      ... and {len(not_in_tracker) - 15} more")

    # Step 5: Summary
    print("\n" + "="*120)
    print("SUMMARY:")
    print("="*120)
    print(f"Tracker sheet coverage: {len(found)}/{len(markaz_employees)} employees ({100*len(found)//len(markaz_employees)}%)")
    print(f"Missing from tracker: {len(not_in_tracker)} employees")
    print(f"Not found in Markaz: {len(missing)} names (likely new/typos)")

    print("\n" + "="*120)
    print("NEXT STEP:")
    print("="*120)
    print("\nReady to create CLEAN HIERARCHY sheet with:")
    print("  • Department-based organization")
    print("  • Team Lead → Subordinates (clear hierarchy)")
    print("  • Levels for each person")
    print("  • Easy-to-read structure")
    print("\nShould I create the reorganized sheet? (yes/no)")

if __name__ == "__main__":
    main()
