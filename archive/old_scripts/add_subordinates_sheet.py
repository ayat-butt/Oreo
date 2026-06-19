#!/usr/bin/env python3
"""
Create a new sub-sheet with all subordinates and their levels.
Add it to the existing Google Sheet file.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime
from hr_assistant.config import get_google_services

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")
SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
GID = "654305400"

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
        range=f"'{sheet_name}'!A1:G200"
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
    if len(parts) >= 2:
        for emp in markaz_employees:
            emp_parts = normalize_name(emp["full_name"]).split()
            if any(part in emp_parts for part in parts):
                return emp
    return None

def extract_team_leads(tracker_rows):
    """Extract all team leads from tracker sheet."""
    team_leads = set()
    for row in tracker_rows[1:]:
        if len(row) > 2 and row[2]:  # Team Lead column
            name = str(row[2]).strip()
            if name and not name.startswith("#"):
                team_leads.add(name)
    return team_leads

def extract_subordinates(tracker_rows):
    """Extract all subordinates from Team Member column."""
    subordinates = {}  # {subordinate_name: team_lead}

    for row in tracker_rows[1:]:
        team_lead = row[2] if len(row) > 2 else ""
        team_members = row[6] if len(row) > 6 else ""  # After Level column

        if team_members:
            for member in str(team_members).split(","):
                member = member.strip()
                if member and not member.startswith("#"):
                    subordinates[member] = team_lead

    return subordinates

def create_subordinates_sheet(services, markaz_employees, tracker_rows):
    """Create a new sub-sheet with all subordinates and levels."""
    sheets = services["sheets"]
    drive = services["drive"]

    # Extract all subordinates and their team leads
    subordinates_dict = extract_subordinates(tracker_rows)

    print(f"\n[1] Found {len(subordinates_dict)} subordinates in tracker")

    # Build rows with levels from Markaz
    header = ["Subordinate Name", "Level", "Job Title", "Department", "Team Lead", "Manager"]
    rows = [header]

    for sub_name in sorted(subordinates_dict.keys()):
        emp = find_employee(sub_name, markaz_employees)

        if emp:
            level = emp.get("level") or "—"
            title = emp.get("job_title") or "—"
            dept = emp.get("department") or "—"
            mgr = emp.get("manager_name") or "—"
        else:
            level = "—"
            title = "—"
            dept = "—"
            mgr = "—"

        team_lead = subordinates_dict[sub_name]

        rows.append([
            sub_name,
            level,
            title,
            dept,
            team_lead,
            mgr
        ])

    print(f"[2] Created {len(rows)-1} subordinate rows with levels")

    # Create new sheet in the same spreadsheet
    sheet_body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": "Subordinates",
                        "gridProperties": {"rowCount": 1000, "columnCount": 6}
                    }
                }
            }
        ]
    }

    response = sheets.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body=sheet_body
    ).execute()

    new_sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]
    print(f"[3] Created new sheet 'Subordinates' (ID: {new_sheet_id})")

    # Write data to new sheet
    sheets.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range="'Subordinates'!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    print(f"[4] Wrote {len(rows)} rows to Subordinates sheet")

    # Format header
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": new_sheet_id,
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
                        "sheetId": new_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 6,
                    }
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": new_sheet_id,
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]},
    ).execute()

    print(f"[5] Formatted header")

    return len(rows) - 1

def main():
    print("="*100)
    print("CREATING SUBORDINATES SUB-SHEET")
    print("="*100)

    print("\n[Step 1] Loading Markaz data...")
    markaz_employees = fetch_markaz_data()
    print(f"         ✓ {len(markaz_employees)} employees")

    print("\n[Step 2] Reading tracker sheet...")
    tracker_rows, sheet_name = read_tracker_sheet()
    print(f"         ✓ {len(tracker_rows)} rows")

    print("\n[Step 3] Connecting to Google...")
    services = get_google_services()

    print("\n[Step 4] Creating Subordinates sub-sheet...")
    sub_count = create_subordinates_sheet(services, markaz_employees, tracker_rows)

    print("\n" + "="*100)
    print("✓ SUB-SHEET CREATED SUCCESSFULLY!")
    print("="*100)
    print(f"\nNew sheet details:")
    print(f"  Name: Subordinates")
    print(f"  Rows: {sub_count} subordinates")
    print(f"  Columns: Subordinate Name | Level | Job Title | Department | Team Lead | Manager")
    print(f"\nFile: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
    print(f"\nStructure:")
    print(f"  • Team Leads (Main sheet) - with their levels")
    print(f"  • Subordinates (New tab) - with all subordinates + levels")

if __name__ == "__main__":
    main()
