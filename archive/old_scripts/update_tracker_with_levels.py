#!/usr/bin/env python3
"""
Update the tracker sheet with:
1. Add 16 missing employees
2. Add Level column with levels from Markaz
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
GID = "654305400"

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

def read_tracker_sheet():
    """Read the current tracker sheet."""
    services = get_google_services()
    sheets = services["sheets"]

    metadata = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == GID:
            sheet_name = sheet["properties"]["title"]
            break

    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1:F200"
    ).execute()

    return result.get("values", []), sheet_name

def normalize_name(name):
    """Normalize name for matching."""
    return name.lower().strip().replace("  ", " ")

def find_employee(name, markaz_employees):
    """Find employee in Markaz data."""
    if not name:
        return None
    name_norm = normalize_name(name)
    for emp in markaz_employees:
        if normalize_name(emp["full_name"]) == name_norm:
            return emp
    # Try partial match
    parts = name_norm.split()
    for emp in markaz_employees:
        emp_parts = normalize_name(emp["full_name"]).split()
        if len(parts) >= 2 and any(part in emp_parts for part in parts):
            return emp
    return None

def get_level(name, markaz_employees):
    """Get level for a person."""
    emp = find_employee(name, markaz_employees)
    return emp.get("level") or "—" if emp else "—"

def main():
    print("="*100)
    print("UPDATING TRACKER SHEET")
    print("="*100)

    print("\n[1] Loading Markaz data...")
    markaz_employees = fetch_markaz_data()
    print(f"    ✓ {len(markaz_employees)} employees")

    print("\n[2] Reading current tracker sheet...")
    tracker_rows, sheet_name = read_tracker_sheet()
    print(f"    ✓ {len(tracker_rows)} rows")

    # Identify missing employees
    tracker_names = set()
    for row in tracker_rows[1:]:
        for col_idx in [1, 2, 3, 4]:
            if len(row) > col_idx:
                cell = str(row[col_idx]).strip()
                if not cell or cell.startswith("#"):
                    continue
                if col_idx == 4:
                    for name in cell.split(","):
                        name = name.strip()
                        if name:
                            tracker_names.add(name)
                elif cell:
                    tracker_names.add(cell)

    missing_employees = []
    for emp in markaz_employees:
        emp_name_norm = normalize_name(emp["full_name"])
        found = False
        for tracker_name in tracker_names:
            if normalize_name(tracker_name) == emp_name_norm:
                found = True
                break
        if not found:
            missing_employees.append(emp)

    print(f"    ✓ {len(missing_employees)} employees missing")

    # Build new sheet with levels
    print("\n[3] Building updated sheet with levels...")

    # New header with Level column inserted after "Reports To"
    header = tracker_rows[0] if tracker_rows else []
    # Current: Department | SMT | Team Lead | Reports To | Team Member | # Members
    # New:    Department | SMT | Team Lead | Reports To | Level | Team Member | # Members

    if len(header) < 6:
        header = ["Department", "SMT", "Team Lead", "Reports To", "Team Member", "# Members"]

    # Insert Level column after Reports To (index 3)
    new_header = header[:4] + ["Level"] + header[4:]

    new_rows = [new_header]

    # Process existing rows and add levels
    for row_idx, row in enumerate(tracker_rows[1:], start=2):
        new_row = []

        # Columns 0-3: Department, SMT, Team Lead, Reports To
        for i in range(4):
            new_row.append(row[i] if i < len(row) else "")

        # Column 4: Level (for Team Lead or SMT)
        level = "—"
        if len(row) > 2 and row[2]:  # Team Lead column
            level = get_level(row[2], markaz_employees)
        elif len(row) > 1 and row[1]:  # SMT column
            level = get_level(row[1], markaz_employees)

        new_row.append(level)

        # Columns 5+: Team Member, # Members (shifted due to Level column)
        for i in range(4, len(row)):
            new_row.append(row[i])

        new_rows.append(new_row)

    print(f"    ✓ Added Level column to {len(new_rows)-1} rows")

    # Add missing employees as new rows at the end
    print(f"\n[4] Adding {len(missing_employees)} missing employees...")

    for emp in sorted(missing_employees, key=lambda x: x["full_name"]):
        dept = emp.get("department") or "—"
        name = emp["full_name"]
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

    print(f"    ✓ {len(missing_employees)} rows added")

    # Update the sheet in Google
    print("\n[5] Updating Google Sheet...")
    services = get_google_services()
    sheets = services["sheets"]

    # Clear and write new data
    sheets.spreadsheets().values().clear(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1:Z300"
    ).execute()

    sheets.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1",
        valueInputOption="RAW",
        body={"values": new_rows},
    ).execute()

    print(f"    ✓ Sheet updated ({len(new_rows)} total rows)")

    # Format header
    print("\n[6] Formatting header...")
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": int(GID),
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
                        "sheetId": int(GID),
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 7,
                    }
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": int(GID),
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]},
    ).execute()

    print(f"    ✓ Formatted header")

    print("\n" + "="*100)
    print("✓ UPDATE COMPLETE!")
    print("="*100)
    print(f"\nUpdates applied:")
    print(f"  • Total rows: {len(new_rows)} (was {len(tracker_rows)})")
    print(f"  • New employees added: {len(missing_employees)}")
    print(f"  • Levels added: {len(new_rows)-1}")
    print(f"  • Header modified: Added 'Level' column after 'Reports To'")
    print(f"\nSheet link: https://docs.google.com/spreadsheets/d/{SHEET_ID}")

if __name__ == "__main__":
    main()
