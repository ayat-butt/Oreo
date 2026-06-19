#!/usr/bin/env python3
"""
ULTIMATE THOROUGH CHECK:
- Read EVERY column from tracker sheet
- Extract EVERY name mentioned (Team Lead, Team Members, Reports To, SMT)
- Cross-check against the 39 remaining "missing"
- Use fuzzy matching and variations
- Only report TRUE missing
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from difflib import SequenceMatcher
from hr_assistant.config import get_google_services

TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

# The 39 remaining "missing"
REMAINING_MISSING = [
    "Alamgeer Abbas", "Ali Sipra", "Arbab Abdul Khalil", "Ayat Butt", "Ayesha Raza",
    "Bibi Raheela", "Fareeda Sanam", "Farheen Foad", "Fatima Khan", "Ghulam Sarwar",
    "Gulraiz Ghaffar", "Hamza Mehmood", "Hamza Razaq", "Hashir Hussain", "Hassan Shahzad",
    "Ifraah Javed", "M. Saim", "Mahreen Rabi", "Maria Kareem", "Maryam Yousaf",
    "Mehreen Hussain", "Mehwish Bibi", "Muhammad Abubakr", "Muhammad Hammad Sarfraz",
    "Muhammad Haris", "Muhammad Muneeb", "Muhammad Umar Raza", "Munira Shah",
    "Ramisha Riaz Sheikh", "Saaim Asif", "Saleh Muhammad", "Sana Ishtiaq", "Shareen Umer",
    "Shoaib ud Din", "Syed Zaamin Abbas", "Syeda Mariam Naqvi", "Tehniat Taqdees",
    "Tehreem batool", "Wajiha Malik"
]

def normalize_name(name):
    """Normalize name."""
    return name.lower().strip().replace("  ", " ")

def similarity(a, b):
    """Calculate string similarity."""
    return SequenceMatcher(None, a, b).ratio()

def find_match(name, candidates, threshold=0.80):
    """Find match with fuzzy matching."""
    name_norm = normalize_name(name)

    # Exact match
    for candidate in candidates:
        if normalize_name(candidate) == name_norm:
            return True, candidate

    # Fuzzy match
    for candidate in candidates:
        if similarity(name_norm, normalize_name(candidate)) > threshold:
            return True, candidate

    return False, None

def read_tracker_sheet_complete():
    """Read ENTIRE tracker sheet - all columns, all rows."""
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
    print("="*140)
    print("ULTIMATE THOROUGH CHECK - EVERY NAME IN TRACKER")
    print("="*140)

    print("\n[1] Reading tracker sheet completely...")
    tracker_rows, sheet_name = read_tracker_sheet_complete()
    print(f"    ✓ {len(tracker_rows)} rows read")

    # Extract EVERY name from EVERY column
    all_tracker_names = []
    name_locations = {}  # {name: [(row_num, column_name)]}

    for row_idx, row in enumerate(tracker_rows[1:], start=2):
        # Column A: Department
        # Column B: SMT
        if len(row) > 1 and row[1]:
            name = str(row[1]).strip()
            if name and not name.startswith("#") and not name.isdigit() and name != "—":
                all_tracker_names.append(name)
                if name not in name_locations:
                    name_locations[name] = []
                name_locations[name].append((row_idx, "SMT"))

        # Column C: Team Lead
        if len(row) > 2 and row[2]:
            name = str(row[2]).strip()
            if name and not name.startswith("#") and not name.isdigit() and name != "—":
                all_tracker_names.append(name)
                if name not in name_locations:
                    name_locations[name] = []
                name_locations[name].append((row_idx, "Team Lead"))

        # Column D: Reports To
        if len(row) > 3 and row[3]:
            name = str(row[3]).strip()
            if name and not name.startswith("#") and not name.isdigit() and name != "—":
                all_tracker_names.append(name)
                if name not in name_locations:
                    name_locations[name] = []
                name_locations[name].append((row_idx, "Reports To"))

        # Column G: Team Members (comma-separated)
        if len(row) > 6 and row[6]:
            for member in str(row[6]).split(","):
                name = member.strip()
                if name and not name.startswith("#") and not name.isdigit() and name != "—":
                    all_tracker_names.append(name)
                    if name not in name_locations:
                        name_locations[name] = []
                    name_locations[name].append((row_idx, "Team Member"))

    unique_tracker_names = list(set(all_tracker_names))
    print(f"    ✓ {len(all_tracker_names)} total name mentions")
    print(f"    ✓ {len(unique_tracker_names)} unique names")

    print(f"\n[2] Cross-checking 39 'missing' against tracker names...")

    found_in_tracker = []
    truly_missing = []

    for missing_name in sorted(REMAINING_MISSING):
        is_match, matched_name = find_match(missing_name, unique_tracker_names, threshold=0.80)

        if is_match:
            locations = name_locations.get(matched_name, [])
            found_in_tracker.append((missing_name, matched_name, locations))
        else:
            truly_missing.append(missing_name)

    print(f"    ✓ {len(found_in_tracker)} FOUND in tracker")
    print(f"    ⚠ {len(truly_missing)} TRULY MISSING")

    # Report found
    if found_in_tracker:
        print("\n" + "="*140)
        print("FOUND IN TRACKER (already present):")
        print("="*140)
        print(f"\nTotal: {len(found_in_tracker)}\n")

        for missing, matched, locations in sorted(found_in_tracker):
            print(f"✓ {missing:<35} → Found as: {matched}")
            for row_num, col_name in locations:
                print(f"      Row {row_num}, {col_name}")

    # Report truly missing
    if truly_missing:
        print("\n" + "="*140)
        print("TRULY MISSING FROM TRACKER:")
        print("="*140)
        print(f"\nTotal: {len(truly_missing)}\n")

        for name in sorted(truly_missing):
            print(f"  • {name}")

    print("\n" + "="*140)
    print("FINAL SUMMARY:")
    print("="*140)
    print(f"\nStarting with: 39 'missing'")
    print(f"  ✓ Already in tracker: {len(found_in_tracker)}")
    print(f"  ⚠ TRULY MISSING: {len(truly_missing)}")

if __name__ == "__main__":
    main()
