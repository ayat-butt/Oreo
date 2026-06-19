#!/usr/bin/env python3
"""Check probation tracker for employees needing action."""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

SHEET_ID = "1_yvL_lM3WzE5BBzsk60PO7gutsYer_y1PSFbTT0hJBY"
GID = "322356645"

def main():
    services = get_google_services()
    sheets = services["sheets"]

    # Get sheet metadata
    metadata = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()

    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == GID:
            sheet_name = sheet["properties"]["title"]
            break

    # Read the entire sheet
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1:M100"
    ).execute()

    rows = result.get("values", [])

    print("=" * 120)
    print("PROBATION TRACKER - ACTION ITEMS (Excluding Ahwaz)")
    print("=" * 120)

    # Find header row
    header_row = None
    for i, row in enumerate(rows):
        if row and "#" in str(row[0]) and "Name" in str(row):
            header_row = i
            break

    if header_row is None:
        print("Could not find header row")
        return

    headers = rows[header_row]
    print(f"\nHeaders: {headers}\n")

    # Check requirement column index
    req_col = None
    closure_col = None
    name_col = None

    for i, h in enumerate(headers):
        if "Requirement" in str(h):
            req_col = i
        if "Probation Closure Status" in str(h):
            closure_col = i
        if "Name" in str(h):
            name_col = i

    print(f"Requirement column: {req_col}")
    print(f"Closure Status column: {closure_col}")
    print(f"Name column: {name_col}\n")
    print("-" * 120)

    # Find rows with "Needed" requirement
    needed_rows = []
    for i in range(header_row + 1, len(rows)):
        row = rows[i]
        if len(row) > req_col and "Needed" in str(row[req_col] if req_col < len(row) else ""):
            if len(row) > name_col and row[name_col]:
                # Skip Ahwaz
                if "Ahwaz" not in str(row[name_col]):
                    needed_rows.append((i, row))

    if needed_rows:
        print(f"\nEmployees with 'Needed' status: {len(needed_rows)}\n")
        for idx, (row_num, row) in enumerate(needed_rows, 1):
            print(f"[{idx}] {row}")
            print()
    else:
        print("No employees with 'Needed' status found")

    # Also check for "Initiated" status
    print("\n" + "-" * 120)
    print("\nEmployees with 'Initiated' status (in progress):\n")

    initiated_rows = []
    for i in range(header_row + 1, len(rows)):
        row = rows[i]
        if len(row) > closure_col and "Initiated" in str(row[closure_col] if closure_col < len(row) else ""):
            if len(row) > name_col and row[name_col]:
                initiated_rows.append((i, row))

    if initiated_rows:
        for idx, (row_num, row) in enumerate(initiated_rows, 1):
            print(f"[{idx}] {row}")
            print()
    else:
        print("No employees with 'Initiated' status")

    print("=" * 120)


if __name__ == "__main__":
    main()
