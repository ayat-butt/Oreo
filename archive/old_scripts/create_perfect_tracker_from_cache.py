#!/usr/bin/env python3
"""
Create perfect tracker from cached data without needing Markaz connection.
Use the tracker sheet structure as reference.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from collections import defaultdict
from hr_assistant.config import get_google_services

TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

def read_tracker_sheet():
    """Read current tracker sheet."""
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

def normalize_name(name):
    """Normalize name."""
    return name.lower().strip().replace("  ", " ")

def main():
    print("="*120)
    print("ANALYZING CURRENT TRACKER FOR DUPLICATES")
    print("="*120)

    print("\n[1] Reading current tracker...")
    rows = read_tracker_sheet()
    print(f"    ✓ {len(rows)} total rows")

    # Extract the structure: which names appear multiple times
    print("\n[2] Building employee directory...")

    # Dictionary to track each person's data
    # {normalized_name: {actual_name, dept, level, manager, rows_where_found}}
    employee_master = defaultdict(lambda: {"occurrences": [], "depts": set(), "levels": set(), "managers": set()})

    for row_idx, row in enumerate(rows[1:], start=2):
        if len(row) < 7:
            continue

        dept = row[0] if row[0] else "—"
        smt = row[1] if len(row) > 1 and row[1] else None
        team_lead = row[2] if len(row) > 2 and row[2] else None
        reports_to = row[3] if len(row) > 3 and row[3] else None
        level = row[4] if len(row) > 4 and row[4] else "—"
        team_members = row[6] if len(row) > 6 and row[6] else None

        # Process SMT
        if smt and str(smt).strip() and not str(smt).strip().isdigit():
            smt_norm = normalize_name(str(smt))
            if smt_norm not in employee_master:
                employee_master[smt_norm]["actual_name"] = str(smt)
            employee_master[smt_norm]["occurrences"].append(("SMT", row_idx, dept))
            employee_master[smt_norm]["depts"].add(dept)
            employee_master[smt_norm]["levels"].add(level)

        # Process Team Lead
        if team_lead and str(team_lead).strip() and not str(team_lead).strip().isdigit():
            tl_norm = normalize_name(str(team_lead))
            if tl_norm not in employee_master:
                employee_master[tl_norm]["actual_name"] = str(team_lead)
            employee_master[tl_norm]["occurrences"].append(("Team Lead", row_idx, dept))
            employee_master[tl_norm]["depts"].add(dept)
            employee_master[tl_norm]["levels"].add(level)
            if reports_to:
                employee_master[tl_norm]["managers"].add(str(reports_to))

        # Process Team Members
        if team_members:
            for member in str(team_members).split(","):
                member = member.strip()
                if member and not member.isdigit() and member != "—":
                    mem_norm = normalize_name(member)
                    if mem_norm not in employee_master:
                        employee_master[mem_norm]["actual_name"] = member
                    employee_master[mem_norm]["occurrences"].append(("Team Member", row_idx, dept))
                    employee_master[mem_norm]["depts"].add(dept)

    print(f"    ✓ {len(employee_master)} unique employees found")

    # Find duplicates
    print("\n[3] Analyzing duplicates...")
    duplicates = {name: data for name, data in employee_master.items() if len(data["occurrences"]) > 1}
    single_entries = {name: data for name, data in employee_master.items() if len(data["occurrences"]) == 1}

    print(f"    ✓ Unique entries (appear once): {len(single_entries)}")
    print(f"    ✓ Duplicate entries (appear multiple times): {len(duplicates)}")

    # Analyze duplicate types
    print("\n[4] Duplicate Analysis:")
    print("-"*120)

    duplicate_list = []
    for name_norm, data in sorted(duplicates.items()):
        actual_name = data.get("actual_name", name_norm)
        occurrences = data["occurrences"]
        depts = ", ".join(sorted(data["depts"]))
        levels = ", ".join(sorted(data["levels"]))

        duplicate_list.append((actual_name, len(occurrences), depts, levels, occurrences))

        if len(duplicate_list) <= 15:  # Show first 15
            print(f"\n{actual_name}")
            print(f"  Appears: {len(occurrences)} times")
            for col_type, row_num, dept in occurrences:
                print(f"    • Row {row_num} ({col_type})")

    if len(duplicates) > 15:
        print(f"\n... and {len(duplicates) - 15} more duplicates")

    print("\n" + "="*120)
    print("SUMMARY:")
    print("="*120)
    print(f"\nTotal rows: {len(rows)}")
    print(f"Total unique employees: {len(employee_master)}")
    print(f"  • Single entry: {len(single_entries)}")
    print(f"  • Multiple entries (duplicates): {len(duplicates)}")
    print(f"\nDuplicate breakdown:")

    # Categorize duplicates
    legitimate = []  # Team leads listed as both Team Lead AND SMT
    junk = []  # Same person in same column multiple times
    same_dept = []  # Same person in different rows, same dept
    diff_dept = []  # Same person in different departments

    for name_norm, data in duplicates.items():
        occurrences = data["occurrences"]
        columns = [o[0] for o in occurrences]
        depts = data["depts"]
        actual_name = data.get("actual_name", name_norm)

        # Check if it's legitimate (Team Lead AND SMT)
        if "Team Lead" in columns and "SMT" in columns and len(columns) == 2:
            legitimate.append(actual_name)
        # Check if different departments
        elif len(depts) > 1:
            diff_dept.append((actual_name, occurrences))
        # Check if same column multiple times (junk)
        elif columns.count(columns[0]) == len(columns):
            junk.append((actual_name, occurrences))
        else:
            same_dept.append((actual_name, occurrences))

    print(f"  ✓ Legitimate (Team Lead + SMT): {len(legitimate)} employees")
    print(f"  ⚠ Different departments: {len(diff_dept)} employees")
    print(f"  ⚠ Same column, multiple rows: {len(same_dept)} employees")
    print(f"  🔴 Junk data: {len(junk)} entries")

    if diff_dept:
        print(f"\n  Different Department Duplicates (Should CONSOLIDATE):")
        for name, occs in diff_dept[:5]:
            print(f"    • {name} - appears in {len(set(o[2] for o in occs))} departments")
        if len(diff_dept) > 5:
            print(f"    ... and {len(diff_dept)-5} more")

    print("\n" + "="*120)
    print("RECOMMENDATION:")
    print("="*120)
    print(f"\nTo create a PERFECT tracker:")
    print(f"  1. Keep {len(legitimate)} legitimate team lead duplicates (Team Lead + SMT)")
    print(f"  2. Consolidate {len(diff_dept)} employees appearing in different departments")
    print(f"  3. Remove {len(same_dept)} entries that are true duplicates in same column")
    print(f"  4. Remove {len(junk)} junk entries")
    print(f"\nResult: {len(employee_master)} → {len(single_entries) + len(legitimate) + len(diff_dept)} clean employees")

if __name__ == "__main__":
    main()
