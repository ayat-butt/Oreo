"""Update missing joining dates for Muhammad Ahmed and Mohammed Raiyaan Junaid Hamid."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from datetime import datetime
from hr_assistant.config import get_google_services

services = get_google_services()
sheets = services["sheets"]

SHEET_ID = "1_yvL_lM3WzE5BBzsk60PO7gutsYer_y1PSFbTT0hJBY"
TAB_GID = 322356645

# Read current sheet
result = sheets.spreadsheets().values().get(
    spreadsheetId=SHEET_ID,
    range="'Probation Tracker'!A:L"
).execute()

rows = result.get("values", [])
print(f"Read {len(rows)} rows from sheet")

# Find rows to update
updates = []
for i, row in enumerate(rows[1:], start=2):  # Skip header
    if len(row) > 1:
        name = row[1] if len(row) > 1 else ""
        if "Muhammad Ahmed" in name:
            print(f"Row {i}: {name} → joining_date = 1 June 2026")
            updates.append({
                "range": f"'Probation Tracker'!F{i}",
                "values": [["1 June 2026"]]
            })
        elif "Mohammed Raiyaan" in name:
            print(f"Row {i}: {name} → joining_date = 3 June 2026")
            updates.append({
                "range": f"'Probation Tracker'!F{i}",
                "values": [["3 June 2026"]]
            })

if updates:
    print(f"\nUpdating {len(updates)} rows...")
    data = {"data": updates, "valueInputOption": "RAW"}
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID,
        body=data
    ).execute()
    print("✓ Updated successfully")
else:
    print("No employees found to update")
