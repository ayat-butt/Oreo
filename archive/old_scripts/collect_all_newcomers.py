#!/usr/bin/env python3
"""Collect all newcomers from all months in edition/deletion sheet."""

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
EDITION_SHEET_ID = "18x6R4Gl3P_D-Dn_HHtLpXbpwQnqVafO6rekvovcVICk"
TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

def get_all_sheets():
    """Get all sheet tabs from edition/deletion file."""
    services = get_google_services()
    sheets = services["sheets"]

    metadata = sheets.spreadsheets().get(spreadsheetId=EDITION_SHEET_ID).execute()

    sheet_list = []
    for sheet in metadata.get("sheets", []):
        title = sheet["properties"]["title"]
        sheet_id = sheet["properties"]["sheetId"]
        sheet_list.append((title, sheet_id))

    return sheet_list

def read_additions_from_month(sheet_name):
    """Read employee additions from a specific month."""
    services = get_google_services()
    sheets = services["sheets"]

    result = sheets.spreadsheets().values().get(
        spreadsheetId=EDITION_SHEET_ID,
        range=f"'{sheet_name}'!A1:B100"
    ).execute()

    rows = result.get("values", [])
    additions = []

    # Find "Employee Addition" section
    found_addition = False
    for row in rows:
        if row and "Employee Addition" in str(row[0]):
            found_addition = True
            continue

        if found_addition and row:
            name = str(row[0]).strip()
            if name and name.lower() != "name" and name:
                additions.append(name)

    return additions

def fetch_markaz_data():
    """Fetch all employees from Markaz."""
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
    """Read the hierarchy tracker sheet."""
    services = get_google_services()
    sheets = services["sheets"]

    metadata = sheets.spreadsheets().get(spreadsheetId=TRACKER_SHEET_ID).execute()
    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == TRACKER_GID:
            sheet_name = sheet["properties"]["title"]
            break

    result = sheets.spreadsheets().values().get(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'{sheet_name}'!A1:G200"
    ).execute()

    return result.get("values", [])

def normalize_name(name):
    """Normalize name for matching."""
    return name.lower().strip().replace("  ", " ")

def find_in_tracker(name, tracker_rows):
    """Check if name exists in tracker sheet."""
    name_norm = normalize_name(name)
    for row in tracker_rows:
        for col in row:
            if normalize_name(str(col)) == name_norm:
                return True
    return False

def find_in_markaz(name, markaz_employees):
    """Find employee in Markaz."""
    name_norm = normalize_name(name)
    for emp in markaz_employees:
        if normalize_name(emp["full_name"]) == name_norm:
            return emp
    return None

def main():
    print("="*120)
    print("COLLECTING ALL NEWCOMERS FROM EDITION/DELETION SHEET")
    print("="*120)

    print("\n[1] Getting all month tabs...")
    all_sheets = get_all_sheets()
    print(f"    ✓ {len(all_sheets)} months found")

    print("\n[2] Reading employee additions from each month...")
    all_additions = set()
    additions_by_month = {}

    for sheet_name, sheet_id in all_sheets:
        additions = read_additions_from_month(sheet_name)
        if additions:
            additions_by_month[sheet_name] = additions
            all_additions.update(additions)
            print(f"    {sheet_name:<20} : {len(additions)} addition(s)")

    print(f"\n    ✓ Total unique newcomers found: {len(all_additions)}")

    print("\n[3] Loading Markaz data...")
    markaz_employees = fetch_markaz_data()
    print(f"    ✓ {len(markaz_employees)} employees in Markaz")

    print("\n[4] Reading tracker sheet...")
    tracker_rows = read_tracker_sheet()
    print(f"    ✓ {len(tracker_rows)} rows in tracker")

    print("\n[5] Cross-checking additions...")
    missing_from_tracker = []
    already_in_tracker = []
    not_in_markaz = []

    for name in sorted(all_additions):
        in_tracker = find_in_tracker(name, tracker_rows)
        in_markaz = find_in_markaz(name, markaz_employees)

        if not in_tracker and in_markaz:
            missing_from_tracker.append((name, in_markaz))
        elif in_tracker:
            already_in_tracker.append(name)
        elif not in_markaz:
            not_in_markaz.append(name)

    print(f"    ✓ {len(already_in_tracker)} already in tracker")
    print(f"    ⚠ {len(missing_from_tracker)} missing from tracker (but in Markaz)")
    print(f"    ⚠ {len(not_in_markaz)} not found in Markaz")

    # Show missing employees
    if missing_from_tracker:
        print("\n" + "="*120)
        print("NEWCOMERS MISSING FROM TRACKER (but exist in Markaz):")
        print("="*120)
        print(f"\n{'#':<3} {'Name':<35} {'Level':<10} {'Manager':<35} {'Department':<25}")
        print("-"*120)

        for idx, (name, emp) in enumerate(sorted(missing_from_tracker, key=lambda x: x[0]), 1):
            level = emp.get("level") or "—"
            mgr = emp.get("manager_name") or "—"
            dept = emp.get("department") or "—"
            print(f"{idx:<3} {name:<35} {level:<10} {mgr:<35} {dept:<25}")

    # Show not in Markaz
    if not_in_markaz:
        print("\n" + "="*120)
        print("NEWCOMERS NOT FOUND IN MARKAZ (may need to be added to Markaz):")
        print("="*120)
        for name in sorted(not_in_markaz):
            print(f"  • {name}")

    # Show already in tracker
    if already_in_tracker:
        print("\n" + "="*120)
        print(f"NEWCOMERS ALREADY IN TRACKER ({len(already_in_tracker)}):")
        print("="*120)
        for name in sorted(already_in_tracker)[:10]:
            print(f"  ✓ {name}")
        if len(already_in_tracker) > 10:
            print(f"  ... and {len(already_in_tracker) - 10} more")

    print("\n" + "="*120)
    print("SUMMARY:")
    print("="*120)
    print(f"\nTotal newcomers in edition/deletion sheet: {len(all_additions)}")
    print(f"  ✓ Already in tracker: {len(already_in_tracker)}")
    print(f"  ⚠ Missing from tracker (need to add): {len(missing_from_tracker)}")
    print(f"  ⚠ Not in Markaz: {len(not_in_markaz)}")
    print(f"\nShould I add the {len(missing_from_tracker)} missing newcomers to the tracker? (yes/no)")

if __name__ == "__main__":
    main()
