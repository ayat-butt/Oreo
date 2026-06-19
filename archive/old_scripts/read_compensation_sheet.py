#!/usr/bin/env python3
"""Read the compensation review sheet to see its structure and levels."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

# Compensation review sheet
COMP_SHEET_ID = "1a0Y2iYXIgNQH-ooUo0blewi4VksUI353nh0Wo4pvs7A"
COMP_GID = "1635039725"

def main():
    print("Reading compensation review sheet...\n")

    services = get_google_services()
    sheets = services["sheets"]

    # Get sheet metadata
    metadata = sheets.spreadsheets().get(spreadsheetId=COMP_SHEET_ID).execute()

    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == COMP_GID:
            sheet_name = sheet["properties"]["title"]
            break

    print(f"Sheet name: {sheet_name}\n")

    # Read the sheet
    result = sheets.spreadsheets().values().get(
        spreadsheetId=COMP_SHEET_ID,
        range=f"'{sheet_name}'!A1:Z100"
    ).execute()

    rows = result.get("values", [])

    if not rows:
        print("Sheet is empty")
        return

    # Print header
    print("=" * 150)
    print("HEADER ROW:")
    print("=" * 150)
    header = rows[0]
    for i, col in enumerate(header):
        print(f"  [{i}] {col}")
    print()

    # Print first 10 rows to see structure
    print("=" * 150)
    print("SAMPLE DATA (first 10 rows):")
    print("=" * 150)
    for row_idx, row in enumerate(rows[1:11], start=2):
        print(f"\nRow {row_idx}:")
        for col_idx, col_name in enumerate(header):
            val = row[col_idx] if col_idx < len(row) else ""
            print(f"  {col_name}: {val}")

if __name__ == "__main__":
    main()
