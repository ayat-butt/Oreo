#!/usr/bin/env python3
"""
Thorough check for TRULY missing employees.
- Check ALL columns: SMT, Team Lead, Team Members
- Account for name variations/typos
- Use fuzzy matching
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from difflib import SequenceMatcher
from hr_assistant.config import get_google_services

TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"
EDITION_SHEET_ID = "18x6R4Gl3P_D-Dn_HHtLpXbpwQnqVafO6rekvovcVICk"

def normalize_name(name):
    """Normalize name."""
    return name.lower().strip().replace("  ", " ")

def similarity(a, b):
    """Calculate string similarity (0-1)."""
    return SequenceMatcher(None, a, b).ratio()

def fuzzy_match(name, candidates, threshold=0.75):
    """Find if name matches any candidate with fuzzy matching."""
    name_norm = normalize_name(name)

    for candidate in candidates:
        candidate_norm = normalize_name(candidate)

        # Exact match
        if name_norm == candidate_norm:
            return True, candidate

        # Fuzzy match (similarity > threshold)
        if similarity(name_norm, candidate_norm) > threshold:
            return True, candidate

    return False, None

def read_tracker_sheet():
    """Read tracker sheet - ALL cells."""
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

def get_all_additions():
    """Get all additions from Edition/Deletion."""
    services = get_google_services()
    sheets = services["sheets"]

    metadata = sheets.spreadsheets().get(spreadsheetId=EDITION_SHEET_ID).execute()

    all_additions = set()

    for sheet in metadata.get("sheets", []):
        sheet_name = sheet["properties"]["title"]

        result = sheets.spreadsheets().values().get(
            spreadsheetId=EDITION_SHEET_ID,
            range=f"'{sheet_name}'!A1:B100"
        ).execute()

        rows = result.get("values", [])

        found_addition = False
        for row in rows:
            if row and "Employee Addition" in str(row[0]):
                found_addition = True
                continue

            if found_addition and row:
                name = str(row[0]).strip()
                if name and name.lower() != "name" and name and not name.startswith("#"):
                    all_additions.add(name)

    return all_additions

def main():
    print("="*120)
    print("THOROUGH CHECK: ALL COLUMNS + FUZZY MATCHING")
    print("="*120)

    print("\n[1] Reading tracker sheet (all cells)...")
    tracker_rows = read_tracker_sheet()

    # Collect ALL names from ALL columns
    tracker_all_names = []

    for row_idx, row in enumerate(tracker_rows[1:], start=2):
        # Column B: SMT
        if len(row) > 1 and row[1]:
            name = str(row[1]).strip()
            if name and not name.startswith("#") and not name.isdigit() and name != "—":
                tracker_all_names.append(name)

        # Column C: Team Lead
        if len(row) > 2 and row[2]:
            name = str(row[2]).strip()
            if name and not name.startswith("#") and not name.isdigit() and name != "—":
                tracker_all_names.append(name)

        # Column G: Team Members (THIS IS KEY!)
        if len(row) > 6 and row[6]:
            for member in str(row[6]).split(","):
                name = member.strip()
                if name and not name.startswith("#") and not name.isdigit() and name != "—":
                    tracker_all_names.append(name)

    print(f"    ✓ {len(tracker_all_names)} total names in tracker (including team members)")
    print(f"    ✓ {len(set(tracker_all_names))} unique names")

    print("\n[2] Reading Edition/Deletion additions...")
    all_additions = get_all_additions()
    print(f"    ✓ {len(all_additions)} additions found")

    print("\n[3] Fuzzy matching additions against tracker...")

    truly_missing = []
    found_with_match = []

    for added_name in sorted(all_additions):
        is_match, matched_name = fuzzy_match(added_name, tracker_all_names, threshold=0.75)

        if is_match:
            found_with_match.append((added_name, matched_name))
        else:
            truly_missing.append(added_name)

    print(f"    ✓ {len(found_with_match)} found with fuzzy matching")
    print(f"    ⚠ {len(truly_missing)} TRULY MISSING")

    if found_with_match:
        print("\n" + "="*120)
        print("NAME VARIATIONS FOUND (Present in sheet but spelled differently):")
        print("="*120)
        print(f"\nTotal: {len(found_with_match)}\n")

        for added, matched in sorted(found_with_match)[:20]:
            print(f"  ✓ {added:<40} → Found as: {matched}")

        if len(found_with_match) > 20:
            print(f"\n  ... and {len(found_with_match) - 20} more matches")

    if truly_missing:
        print("\n" + "="*120)
        print("TRULY MISSING EMPLOYEES (Not in tracker at all):")
        print("="*120)
        print(f"\nTotal: {len(truly_missing)}\n")

        for name in truly_missing:
            print(f"  • {name}")

    print("\n" + "="*120)
    print("FINAL SUMMARY:")
    print("="*120)
    print(f"\nEdition/Deletion additions: {len(all_additions)}")
    print(f"  ✓ Found in tracker (with variations): {len(found_with_match)}")
    print(f"  ⚠ TRULY MISSING: {len(truly_missing)}")

if __name__ == "__main__":
    main()
