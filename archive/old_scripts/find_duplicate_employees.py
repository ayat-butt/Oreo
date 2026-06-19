#!/usr/bin/env python3
"""Find and highlight duplicate employee entries in tracker sheet."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from collections import defaultdict
from hr_assistant.config import get_google_services

TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

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

    return result.get("values", []), sheet_name

def main():
    print("="*120)
    print("FINDING DUPLICATE EMPLOYEE ENTRIES")
    print("="*120)

    print("\n[1] Reading tracker sheet...")
    tracker_rows, sheet_name = read_tracker_sheet()
    print(f"    ✓ {len(tracker_rows)} total rows")

    # Extract all names and their row numbers
    print("\n[2] Extracting all employee names...")

    name_rows = defaultdict(list)  # {normalized_name: [(actual_name, row_number, column)]}
    all_names = []

    for row_idx, row in enumerate(tracker_rows[1:], start=2):  # Skip header
        # Column B: SMT
        if len(row) > 1 and row[1]:
            name = str(row[1]).strip()
            if name and not name.startswith("#"):
                name_norm = normalize_name(name)
                name_rows[name_norm].append((name, row_idx, "SMT (B)"))
                all_names.append(name)

        # Column C: Team Lead
        if len(row) > 2 and row[2]:
            name = str(row[2]).strip()
            if name and not name.startswith("#"):
                name_norm = normalize_name(name)
                name_rows[name_norm].append((name, row_idx, "Team Lead (C)"))
                all_names.append(name)

        # Column G: Team Members
        if len(row) > 6 and row[6]:
            for member in str(row[6]).split(","):
                name = member.strip()
                if name and not name.startswith("#"):
                    name_norm = normalize_name(name)
                    name_rows[name_norm].append((name, row_idx, "Team Member (G)"))
                    all_names.append(name)

    print(f"    ✓ {len(all_names)} total names extracted")
    print(f"    ✓ {len(name_rows)} unique names (normalized)")

    # Find duplicates
    print("\n[3] Identifying duplicates...")
    duplicates = {}
    for name_norm, occurrences in name_rows.items():
        if len(occurrences) > 1:
            duplicates[name_norm] = occurrences

    print(f"    ✓ Found {len(duplicates)} duplicate names")

    if duplicates:
        print("\n" + "="*120)
        print("DUPLICATE ENTRIES FOUND:")
        print("="*120)

        for idx, (name_norm, occurrences) in enumerate(sorted(duplicates.items()), 1):
            print(f"\n[{idx}] {name_norm.upper()}")
            print(f"    Appears {len(occurrences)} times:")
            for actual_name, row_num, column in occurrences:
                print(f"      • Row {row_num:<3} | Column {column:<20} | Name: {actual_name}")

        # Summary
        total_duplicate_rows = sum(len(occs) for occs in duplicates.values())
        print(f"\n" + "="*120)
        print("SUMMARY:")
        print("="*120)
        print(f"\nDuplicate names: {len(duplicates)}")
        print(f"Total duplicate entries: {total_duplicate_rows}")
        print(f"Unique employees: {len(name_rows) - len(duplicates)}")

        # Calculate unique count
        unique_employees = len(name_rows)
        print(f"\nTotal UNIQUE employees: {unique_employees}")
        print(f"Total entries (including duplicates): {len(all_names)}")
        print(f"Duplicate entries to remove: {len(all_names) - unique_employees}")

    else:
        print("\n" + "="*120)
        print("✓ NO DUPLICATES FOUND!")
        print("="*120)
        print(f"\nTotal UNIQUE employees: {len(name_rows)}")
        print(f"Total entries: {len(all_names)}")

if __name__ == "__main__":
    main()
