#!/usr/bin/env python3
"""Read the hierarchy tracker sheet to see current structure."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

# The tracker sheet URL you provided
SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
GID = "654305400"

def main():
    print("Fetching hierarchy tracker sheet...\n")

    services = get_google_services()
    sheets = services["sheets"]

    # Get sheet metadata to find the sheet name
    metadata = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()

    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == GID:
            sheet_name = sheet["properties"]["title"]
            break

    if not sheet_name:
        print(f"Could not find sheet with gid {GID}")
        return

    print(f"Sheet name: {sheet_name}\n")

    # Read the entire sheet
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1:Z200"
    ).execute()

    rows = result.get("values", [])

    if not rows:
        print("Sheet is empty")
        return

    # Print header row
    print("=" * 150)
    print("HEADER ROW:")
    print("=" * 150)
    header = rows[0]
    for i, col in enumerate(header):
        print(f"  [{i}] {col}")
    print()

    # Print all data rows
    print("=" * 150)
    print(f"DATA ROWS ({len(rows)-1} rows):")
    print("=" * 150)
    for row_idx, row in enumerate(rows[1:], start=2):
        print(f"\nRow {row_idx}:")
        for col_idx, col in enumerate(header):
            val = row[col_idx] if col_idx < len(row) else ""
            print(f"  {col}: {val}")

if __name__ == "__main__":
    main()
