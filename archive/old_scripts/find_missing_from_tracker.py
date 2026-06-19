#!/usr/bin/env python3
"""
Compare tracker sheet with Edition/Deletion sheet.
Find any employees/team leads/members missing from tracker.
Only report names - no changes.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from collections import defaultdict
from hr_assistant.config import get_google_services

TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"
EDITION_SHEET_ID = "18x6R4Gl3P_D-Dn_HHtLpXbpwQnqVafO6rekvovcVICk"

def normalize_name(name):
    """Normalize name for matching."""
    return name.lower().strip().replace("  ", " ")

def read_tracker_sheet():
    """Read tracker sheet."""
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
        range=f"'{sheet_name}'!A1:G500"
    ).execute()

    return result.get("values", [])

def get_all_additions_from_edition_sheet():
    """Read ALL additions from Edition/Deletion sheet across all months."""
    services = get_google_services()
    sheets = services["sheets"]

    # Get all sheets
    metadata = sheets.spreadsheets().get(spreadsheetId=EDITION_SHEET_ID).execute()

    all_additions = set()
    additions_by_month = {}

    for sheet in metadata.get("sheets", []):
        sheet_name = sheet["properties"]["title"]

        result = sheets.spreadsheets().values().get(
            spreadsheetId=EDITION_SHEET_ID,
            range=f"'{sheet_name}'!A1:B100"
        ).execute()

        rows = result.get("values", [])

        # Find "Employee Addition" section
        found_addition = False
        month_additions = []
        for row in rows:
            if row and "Employee Addition" in str(row[0]):
                found_addition = True
                continue

            if found_addition and row:
                name = str(row[0]).strip()
                if name and name.lower() != "name" and name and not name.startswith("#"):
                    month_additions.append(name)
                    all_additions.add(name)

        if month_additions:
            additions_by_month[sheet_name] = month_additions

    return all_additions, additions_by_month

def main():
    print("="*120)
    print("COMPARING TRACKER SHEET WITH EDITION/DELETION SHEET")
    print("="*120)

    print("\n[1] Reading tracker sheet...")
    tracker_rows = read_tracker_sheet()
    print(f"    ✓ {len(tracker_rows)} rows read")

    # Extract all names from tracker
    tracker_names = set()
    for row in tracker_rows[1:]:  # Skip header
        # Column B: SMT
        if len(row) > 1 and row[1]:
            name = str(row[1]).strip()
            if name and not name.startswith("#") and not name.isdigit():
                tracker_names.add(name)

        # Column C: Team Lead
        if len(row) > 2 and row[2]:
            name = str(row[2]).strip()
            if name and not name.startswith("#") and not name.isdigit():
                tracker_names.add(name)

        # Column G: Team Members
        if len(row) > 6 and row[6]:
            for member in str(row[6]).split(","):
                name = member.strip()
                if name and not name.startswith("#") and not name.isdigit() and name != "—":
                    tracker_names.add(name)

    print(f"    ✓ {len(tracker_names)} unique employees in tracker")

    print("\n[2] Reading Edition/Deletion sheet...")
    all_additions, additions_by_month = get_all_additions_from_edition_sheet()
    print(f"    ✓ Found {len(additions_by_month)} months with data")
    print(f"    ✓ {len(all_additions)} total unique additions across all months")

    print("\n[3] Cross-checking for missing employees...")

    # Find which additions are NOT in tracker
    missing_from_tracker = []
    already_in_tracker = []

    for added_name in sorted(all_additions):
        added_norm = normalize_name(added_name)
        found = False

        for tracker_name in tracker_names:
            if normalize_name(tracker_name) == added_norm:
                found = True
                break

        if not found:
            missing_from_tracker.append(added_name)
        else:
            already_in_tracker.append(added_name)

    print(f"    ✓ {len(already_in_tracker)} employees already in tracker")
    print(f"    ⚠ {len(missing_from_tracker)} employees MISSING from tracker")

    if missing_from_tracker:
        print("\n" + "="*120)
        print("MISSING EMPLOYEES (Additions not in tracker):")
        print("="*120)
        print(f"\nTotal missing: {len(missing_from_tracker)}\n")

        for idx, name in enumerate(sorted(missing_from_tracker), 1):
            # Find which month they were added
            month_added = None
            for month, names in additions_by_month.items():
                if name in names:
                    month_added = month
                    break

            print(f"{idx:<3} {name:<40} (Added: {month_added})")

    # Also check reverse: are there people in tracker who were deleted?
    print("\n" + "="*120)
    print("ANALYSIS:")
    print("="*120)
    print(f"\nEdition/Deletion Sheet (Additions): {len(all_additions)} employees")
    print(f"Tracker Sheet: {len(tracker_names)} unique employees")
    print(f"\nMissing from tracker: {len(missing_from_tracker)}")
    print(f"Already in tracker: {len(already_in_tracker)}")

    if missing_from_tracker:
        print(f"\n⚠️  ACTION REQUIRED:")
        print(f"The following {len(missing_from_tracker)} employees are listed as ADDITIONS but")
        print(f"are NOT currently in the tracker sheet:")
        print(f"\nNames to add to tracker:")
        for name in sorted(missing_from_tracker):
            print(f"  • {name}")

if __name__ == "__main__":
    main()
