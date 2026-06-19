#!/usr/bin/env python3
"""Check the Google Sheet and see what needs updating for Ahwaz Akhtar."""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

SHEET_ID = "1_yvL_lM3WzE5BBzsk60PO7gutsYer_y1PSFbTT0hJBY"
GID = "322356645"

def main():
    services = get_google_services()
    sheets = services["sheets"]

    print("Fetching sheet information...")

    # Get sheet metadata to see the name
    metadata = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()

    # Find the sheet with the matching gid
    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == GID:
            sheet_name = sheet["properties"]["title"]
            break

    print(f"Sheet Name: {sheet_name}")
    print(f"Sheet ID: {SHEET_ID}")
    print(f"GID: {GID}\n")

    # Read the first 50 rows to see the data
    if sheet_name:
        result = sheets.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=f"'{sheet_name}'!A1:Z50"
        ).execute()

        rows = result.get("values", [])

        if rows:
            print(f"Sheet has {len(rows)} rows of data:\n")
            print("-" * 100)

            # Print header row
            if rows:
                headers = rows[0]
                print("Headers:", headers)
                print("-" * 100)

            # Print all rows
            for i, row in enumerate(rows[:20], 1):  # Show first 20 rows
                print(f"Row {i}: {row}")

            if len(rows) > 20:
                print(f"\n... and {len(rows) - 20} more rows")

            print("\n" + "-" * 100)
            print("\nLooking for 'Ahwaz Akhtar'...")
            found = False
            for i, row in enumerate(rows):
                for cell in row:
                    if isinstance(cell, str) and "Ahwaz" in cell:
                        print(f"Found at Row {i+1}: {row}")
                        found = True

            if not found:
                print("Ahwaz Akhtar not found in sheet")
        else:
            print("Sheet is empty")

if __name__ == "__main__":
    main()
