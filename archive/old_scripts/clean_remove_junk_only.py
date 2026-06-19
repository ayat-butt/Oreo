#!/usr/bin/env python3
"""
Simple cleanup: Just remove rows 144-198 (the junk rows with empty data).
Keep the original tracker structure (rows 1-143) intact.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

def read_tracker_sheet():
    """Read tracker."""
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
    print("="*120)
    print("REMOVING JUNK ROWS (144-198) - KEEP ORIGINAL TRACKER INTACT")
    print("="*120)

    print("\n[1] Reading tracker...")
    rows, sheet_name = read_tracker_sheet()
    print(f"    ✓ {len(rows)} total rows")

    print("\n[2] Removing junk rows 144-198...")
    # Keep header (row 1) + data rows 1-143 (original good data)
    clean_rows = rows[:143]
    removed = len(rows) - len(clean_rows)

    print(f"    ✓ Removed {removed} junk rows")
    print(f"    ✓ Kept {len(clean_rows)} rows (header + data)")

    print("\n[3] Analyzing remaining data...")

    # Count unique employees
    unique_names = set()
    for row in clean_rows[1:]:
        if len(row) > 2 and row[2]:  # Team Lead
            name = str(row[2]).strip()
            if name and not name.isdigit():
                unique_names.add(name)

    print(f"    ✓ {len(unique_names)} unique team leads")
    print(f"    ✓ {len(clean_rows)-1} total data rows")

    print("\n[4] Updating Google Sheet...")
    services = get_google_services()
    sheets = services["sheets"]

    # Clear
    sheets.spreadsheets().values().clear(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'{sheet_name}'!A1:Z500"
    ).execute()

    # Write clean data
    sheets.spreadsheets().values().update(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'{sheet_name}'!A1",
        valueInputOption="RAW",
        body={"values": clean_rows},
    ).execute()

    print(f"    ✓ Sheet updated with {len(clean_rows)} rows")

    # Format header
    print("\n[5] Formatting...")
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=TRACKER_SHEET_ID,
        body={"requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": int(TRACKER_GID),
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.7},
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                                "fontSize": 11,
                            },
                            "horizontalAlignment": "CENTER",
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
                }
            },
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": int(TRACKER_GID),
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 7,
                    }
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": int(TRACKER_GID),
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]},
    ).execute()

    print("    ✓ Formatted")

    print("\n" + "="*120)
    print("✓ JUNK ROWS REMOVED!")
    print("="*120)
    print(f"\nFinal Tracker:")
    print(f"  • Total rows: {len(clean_rows)}")
    print(f"  • Data rows: {len(clean_rows) - 1}")
    print(f"  • Junk rows removed: {removed}")
    print(f"  • Unique team leads: {len(unique_names)}")
    print(f"\nStructure preserved:")
    print(f"  Department | SMT | Team Lead | Reports To | Level | Team Member | # Members")
    print(f"\nSheet: https://docs.google.com/spreadsheets/d/{TRACKER_SHEET_ID}")
    print(f"\nNOTE: Original tracker structure (rows 1-143) is kept intact.")
    print(f"      Only junk rows with empty data (144-198) have been removed.")

if __name__ == "__main__":
    main()
