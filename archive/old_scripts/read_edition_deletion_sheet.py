#!/usr/bin/env python3
"""Read the edition/deletion sheet to find newcomers."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

SHEET_ID = "18x6R4Gl3P_D-Dn_HHtLpXbpwQnqVafO6rekvovcVICk"
GID = "1365091393"

def main():
    print("Reading edition/deletion sheet...\n")

    services = get_google_services()
    sheets = services["sheets"]

    # Get sheet metadata
    metadata = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()

    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == GID:
            sheet_name = sheet["properties"]["title"]
            break

    print(f"Sheet name: {sheet_name}\n")

    # Read the sheet
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1:Z200"
    ).execute()

    rows = result.get("values", [])

    if not rows:
        print("Sheet is empty")
        return

    # Print header
    print("=" * 180)
    print("HEADER ROW:")
    print("=" * 180)
    header = rows[0]
    for i, col in enumerate(header):
        print(f"  [{i}] {col}")
    print()

    # Print all data rows
    print("=" * 180)
    print(f"ALL DATA ROWS ({len(rows)-1} rows):")
    print("=" * 180)

    for row_idx, row in enumerate(rows[1:], start=2):
        print(f"\nRow {row_idx}:")
        for col_idx, col_name in enumerate(header):
            val = row[col_idx] if col_idx < len(row) else ""
            print(f"  {col_name}: {val}")

if __name__ == "__main__":
    main()
