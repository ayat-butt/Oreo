#!/usr/bin/env python3
"""Count current total employees in tracker sheet."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

def main():
    print("Counting current employees in tracker sheet...\n")

    services = get_google_services()
    sheets = services["sheets"]

    # Get sheet metadata
    metadata = sheets.spreadsheets().get(spreadsheetId=TRACKER_SHEET_ID).execute()

    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == TRACKER_GID:
            sheet_name = sheet["properties"]["title"]
            break

    # Read the sheet
    result = sheets.spreadsheets().values().get(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'{sheet_name}'!A1:G500"
    ).execute()

    rows = result.get("values", [])

    print(f"Total rows in sheet: {len(rows)}")
    print(f"Header row: 1")
    print(f"Data rows: {len(rows) - 1}")

    # Count unique employees mentioned
    unique_names = set()

    for row in rows[1:]:  # Skip header
        # Column 1: SMT
        if len(row) > 1 and row[1]:
            name = str(row[1]).strip()
            if name and not name.startswith("#"):
                unique_names.add(name)

        # Column 2: Team Lead
        if len(row) > 2 and row[2]:
            name = str(row[2]).strip()
            if name and not name.startswith("#"):
                unique_names.add(name)

        # Column 6: Team Members
        if len(row) > 6 and row[6]:
            for member in str(row[6]).split(","):
                name = member.strip()
                if name and not name.startswith("#"):
                    unique_names.add(name)

    print(f"\n" + "="*80)
    print("CURRENT TRACKER SHEET STATISTICS:")
    print("="*80)
    print(f"\nTotal unique employees mentioned: {len(unique_names)}")
    print(f"Total rows (including header): {len(rows)}")
    print(f"Data rows: {len(rows) - 1}")

    print(f"\n" + "="*80)
    print("BREAKDOWN:")
    print("="*80)
    print(f"\nTeam Leads (unique): ~{len([r for r in rows[1:] if len(r) > 2 and r[2]])}")
    print(f"Subordinates mentioned: {len(unique_names) - len([r for r in rows[1:] if len(r) > 2 and r[2]])}")

    print(f"\n" + "="*80)
    print("IF YOU ADD 39 MISSING NEWCOMERS:")
    print("="*80)
    print(f"Current unique employees: {len(unique_names)}")
    print(f"+ Missing newcomers: 39")
    print(f"= New total: {len(unique_names) + 39}")

if __name__ == "__main__":
    main()
