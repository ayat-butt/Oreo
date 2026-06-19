#!/usr/bin/env python3
"""
Add the 39 missing newcomers to the tracker sheet.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from hr_assistant.config import get_google_services

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")
TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

# The 39 missing newcomers
MISSING_NEWCOMERS = [
    "Abdul Rehman",
    "Aleeha Noor",
    "Aneela khaliq",
    "Ayat Butt",
    "Bushra",
    "Danish Iqbal",
    "Fakhr Ul Islam",
    "Fatima Khan",
    "Hamza Siddique",
    "Haroon Ali",
    "Hassan Shahzad",
    "Iffat Maab Akhtar",
    "Jamshaid Ahmad",
    "Javeria Khalil",
    "Meerab Din",
    "Mehwish Allah Ditta",
    "Mehwish Bibi",
    "Moiz Khan",
    "Mubashar Zia",
    "Mubasher Irfan",
    "Muhammad Hammad Sarfraz",
    "Muhammad Haris",
    "Muhammad Imran",
    "Muhammad Salman",
    "Muhammad Umar Raza",
    "Nouman Alam",
    "Ramisha Riaz Sheikh",
    "Rida Abbas",
    "Saima Jabeen",
    "Saleh Muhammad",
    "Shareen Umer",
    "Shazmina Sharif",
    "Shoaib ud Din",
    "Sohaib Danish",
    "Syeda Mehwish Ali",
    "Toseef Ur Rehman",
    "Waleed Abdullah",
    "Zainab Zaheer",
    "Zarmeen Kausar",
]

def fetch_markaz_data():
    """Fetch all employees with levels."""
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
            ORDER BY u.first_name, u.last_name
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def normalize_name(name):
    """Normalize name for matching."""
    return name.lower().strip().replace("  ", " ")

def find_employee(name, markaz_employees):
    """Find employee in Markaz."""
    name_norm = normalize_name(name)
    for emp in markaz_employees:
        if normalize_name(emp["full_name"]) == name_norm:
            return emp
    # Try partial match
    parts = name_norm.split()
    if len(parts) >= 2:
        for emp in markaz_employees:
            emp_parts = normalize_name(emp["full_name"]).split()
            if any(part in emp_parts for part in parts):
                return emp
    return None

def read_tracker_sheet():
    """Read tracker sheet."""
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
    print("ADDING 39 MISSING NEWCOMERS TO TRACKER")
    print("="*120)

    print("\n[1] Loading Markaz data...")
    markaz_employees = fetch_markaz_data()
    print(f"    ✓ {len(markaz_employees)} employees")

    print("\n[2] Reading current tracker sheet...")
    tracker_rows, sheet_name = read_tracker_sheet()
    print(f"    ✓ {len(tracker_rows)} rows")

    print("\n[3] Building new rows for missing newcomers...")
    new_rows = []

    for name in MISSING_NEWCOMERS:
        emp = find_employee(name, markaz_employees)
        if emp:
            dept = emp.get("department") or "—"
            level = emp.get("level") or "—"
            mgr = emp.get("manager_name") or "—"

            new_row = [
                dept,      # Department
                "—",       # SMT
                name,      # Team Lead
                mgr,       # Reports To
                level,     # Level
                "—",       # Team Member
                "0"        # # Members
            ]
            new_rows.append(new_row)
            print(f"    ✓ {name:<35} | {level:<10} | {mgr}")
        else:
            print(f"    ✗ {name:<35} | NOT FOUND in Markaz")

    print(f"\n[4] Adding {len(new_rows)} new rows to tracker sheet...")

    services = get_google_services()
    sheets = services["sheets"]

    # Append new rows to the end
    all_rows = tracker_rows + new_rows

    # Clear and write
    sheets.spreadsheets().values().clear(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'{sheet_name}'!A1:Z500"
    ).execute()

    sheets.spreadsheets().values().update(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'{sheet_name}'!A1",
        valueInputOption="RAW",
        body={"values": all_rows},
    ).execute()

    print(f"    ✓ Sheet updated")

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
        ]},
    ).execute()

    print("    ✓ Formatted")

    print("\n" + "="*120)
    print("✓ NEWCOMERS ADDED SUCCESSFULLY!")
    print("="*120)
    print(f"\nSummary:")
    print(f"  Previous rows: {len(tracker_rows)}")
    print(f"  + New rows: {len(new_rows)}")
    print(f"  = Total now: {len(all_rows)}")
    print(f"\nTracker sheet: https://docs.google.com/spreadsheets/d/{TRACKER_SHEET_ID}")

if __name__ == "__main__":
    main()
