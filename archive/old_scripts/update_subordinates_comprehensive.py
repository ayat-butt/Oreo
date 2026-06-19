#!/usr/bin/env python3
"""
Update the Subordinates sheet with ALL employees who have a manager.
Include everyone from Markaz with their levels.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from collections import defaultdict
from hr_assistant.config import get_google_services

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")
SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"

def fetch_markaz_data():
    """Fetch all employees with hierarchy."""
    conn = psycopg2.connect(DB_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT
                u.id,
                u.first_name || ' ' || u.last_name AS full_name,
                ep.level,
                ep.job_title,
                ep.department,
                ep.line_manager_id,
                (SELECT u2.first_name || ' ' || u2.last_name
                 FROM users u2 WHERE u2.id = ep.line_manager_id) AS manager_name
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL AND u.archived_at IS NULL
            ORDER BY COALESCE(ep.department, 'Z-Other'),
                     CASE WHEN ep.level = 'II-B' THEN 1
                          WHEN ep.level = 'II-A' THEN 2
                          WHEN ep.level = 'II-M' THEN 3
                          WHEN ep.level LIKE 'I-%' THEN 4
                          ELSE 5 END,
                     u.first_name, u.last_name
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def main():
    print("="*120)
    print("UPDATING SUBORDINATES SHEET - COMPREHENSIVE")
    print("="*120)

    print("\n[1] Loading Markaz data...")
    all_employees = fetch_markaz_data()
    print(f"    ✓ {len(all_employees)} total employees")

    # Identify subordinates (everyone with a manager)
    subordinates = [emp for emp in all_employees if emp.get("line_manager_id")]
    print(f"    ✓ {len(subordinates)} subordinates (have a manager)")

    # Build rows
    header = ["Subordinate Name", "Level", "Job Title", "Department", "Manager"]
    rows = [header]

    for emp in subordinates:
        rows.append([
            emp["full_name"],
            emp.get("level") or "—",
            emp.get("job_title") or "—",
            emp.get("department") or "—",
            emp.get("manager_name") or "—"
        ])

    print(f"    ✓ Created {len(rows)-1} rows with data")

    # Update Google Sheet
    print("\n[2] Connecting to Google...")
    services = get_google_services()
    sheets = services["sheets"]

    print("\n[3] Clearing old Subordinates sheet...")
    sheets.spreadsheets().values().clear(
        spreadsheetId=SHEET_ID,
        range="'Subordinates'!A1:Z500"
    ).execute()

    print("\n[4] Writing new data...")
    sheets.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range="'Subordinates'!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    print(f"    ✓ Wrote {len(rows)} rows")

    # Get sheet ID and format
    print("\n[5] Formatting...")
    metadata = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sub_sheet_id = None
    for sheet in metadata.get("sheets", []):
        if sheet["properties"]["title"] == "Subordinates":
            sub_sheet_id = sheet["properties"]["sheetId"]
            break

    if sub_sheet_id is not None:
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sub_sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {"red": 0.2, "green": 0.5, "blue": 0.3},
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
                            "sheetId": sub_sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 5,
                        }
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sub_sheet_id,
                            "gridProperties": {"frozenRowCount": 1},
                        },
                        "fields": "gridProperties.frozenRowCount",
                    }
                },
            ]},
        ).execute()
        print("    ✓ Formatted header and columns")

    # Summary
    print("\n" + "="*120)
    print("✓ SUBORDINATES SHEET UPDATED!")
    print("="*120)
    print(f"\nSheet Structure:")
    print(f"  Name: Subordinates")
    print(f"  Rows: {len(rows)-1} subordinates")
    print(f"  Columns: Subordinate Name | Level | Job Title | Department | Manager")
    print(f"\nLevel Distribution in Subordinates:")

    level_count = defaultdict(int)
    for emp in subordinates:
        level = emp.get("level") or "—"
        level_count[level] += 1

    for level in sorted(level_count.keys(), key=lambda x: (x != "II-B", x)):
        print(f"  {level:<15} : {level_count[level]:>3} employees")

    print(f"\nFile: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
    print(f"\nYou now have:")
    print(f"  ✓ Main sheet (Team Leads) - Shows team leads with their levels")
    print(f"  ✓ Subordinates sheet - Shows all {len(rows)-1} subordinates with their levels")

if __name__ == "__main__":
    main()
