#!/usr/bin/env python3
"""
Create a clean, organized hierarchy sheet with:
- Clear Team Lead -> Subordinates structure
- Levels for each person
- Easy-to-understand format
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

def fetch_org_data():
    """Fetch employee data with hierarchy from Markaz."""
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
                ep.line_manager_id
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL AND u.archived_at IS NULL
            ORDER BY u.first_name, u.last_name
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def build_hierarchy(employees):
    """Build manager->subordinates structure."""
    by_id = {e["id"]: e for e in employees if e["id"]}
    manages = defaultdict(list)

    for emp in employees:
        mgr_id = emp.get("line_manager_id")
        if mgr_id and mgr_id in by_id:
            manages[mgr_id].append(emp)

    # Sort subordinates by name
    for mgr_id in manages:
        manages[mgr_id].sort(key=lambda x: x["full_name"])

    return by_id, manages

def find_top_level_managers(by_id, manages):
    """Find managers with no manager (top level)."""
    top_level = []
    for emp in by_id.values():
        if emp.get("line_manager_id") is None or emp.get("line_manager_id") not in by_id:
            if emp["id"] in manages or manages[emp["id"]]:  # Has subordinates
                top_level.append(emp)
    return sorted(top_level, key=lambda x: x["full_name"])

def build_team_structure(manager, manages, by_id, depth=0):
    """Recursively build team structure starting from manager."""
    rows = []
    mgr_id = manager["id"]

    # Manager row
    indent = "  " * depth if depth > 0 else ""
    level = manager.get("level") or "—"
    title = manager.get("job_title") or "—"
    dept = manager.get("department") or "—"

    rows.append([
        indent + manager["full_name"],
        level,
        title,
        dept,
        "Manager" if manages.get(mgr_id) else "Individual Contributor",
        str(len(manages.get(mgr_id, [])))
    ])

    # Subordinates
    for sub in manages.get(mgr_id, []):
        sub_indent = "    " * (depth + 1)
        sub_level = sub.get("level") or "—"
        sub_title = sub.get("job_title") or "—"
        sub_dept = sub.get("department") or "—"

        rows.append([
            sub_indent + sub["full_name"],
            sub_level,
            sub_title,
            sub_dept,
            "Manager" if manages.get(sub["id"]) else "Individual Contributor",
            str(len(manages.get(sub["id"], [])))
        ])

        # Nested subordinates (one level deep for readability)
        for sub_sub in manages.get(sub["id"], []):
            sub_sub_indent = "      " * (depth + 2)
            sub_sub_level = sub_sub.get("level") or "—"
            sub_sub_title = sub_sub.get("job_title") or "—"
            sub_sub_dept = sub_sub.get("department") or "—"

            rows.append([
                sub_sub_indent + sub_sub["full_name"],
                sub_sub_level,
                sub_sub_title,
                sub_sub_dept,
                "Manager" if manages.get(sub_sub["id"]) else "Contributor",
                str(len(manages.get(sub_sub["id"], [])))
            ])

    return rows

def create_clean_sheet(services, employees):
    """Create a new clean hierarchy sheet."""
    sheets = services["sheets"]
    drive = services["drive"]

    by_id, manages = build_hierarchy(employees)
    title = f"Summit Hierarchy — Clean ({datetime.today().strftime('%Y-%m-%d')})"

    # Create new spreadsheet
    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "Hierarchy"}}],
    }).execute()

    sid = spreadsheet["spreadsheetId"]
    shid = spreadsheet["sheets"][0]["properties"]["sheetId"]

    # Build header
    header = ["Name (Team Lead → Subordinates)", "Level", "Job Title", "Department", "Type", "Direct Reports"]

    # Build data rows - organize by top-level managers
    all_rows = [header]

    top_managers = find_top_level_managers(by_id, manages)

    for manager in top_managers:
        team_rows = build_team_structure(manager, manages, by_id)
        all_rows.extend(team_rows)
        all_rows.append(["", "", "", "", "", ""])  # Separator

    # Write to sheet
    sheets.spreadsheets().values().update(
        spreadsheetId=sid,
        range="Hierarchy!A1",
        valueInputOption="RAW",
        body={"values": all_rows},
    ).execute()

    # Format header row
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=sid,
        body={"requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": shid,
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
                            "horizontalAlignment": "LEFT",
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
                }
            },
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": shid,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 6,
                    }
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": shid,
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]},
    ).execute()

    # Get share link
    file_meta = drive.files().get(
        fileId=sid,
        fields="id,name,webViewLink",
    ).execute()

    return {
        "id": sid,
        "title": file_meta["name"],
        "url": file_meta["webViewLink"],
        "rows": len(all_rows),
    }

def main():
    print("Creating clean hierarchy sheet...\n")

    print("[1] Fetching org data from Markaz...")
    employees = fetch_org_data()
    print(f"    ✓ {len(employees)} employees")

    print("\n[2] Building hierarchy structure...")
    by_id, manages = build_hierarchy(employees)
    print(f"    ✓ Hierarchy built")

    print("\n[3] Connecting to Google...")
    services = get_google_services()

    print("\n[4] Creating clean sheet...")
    result = create_clean_sheet(services, employees)

    print("\n" + "="*100)
    print("✓ CLEAN HIERARCHY SHEET CREATED!")
    print("="*100)
    print(f"\nTitle: {result['title']}")
    print(f"Rows:  {result['rows']}")
    print(f"Link:  {result['url']}")
    print("\nFeatures:")
    print("  • Clear hierarchy: Team Lead → Subordinates")
    print("  • Indented structure for easy reading")
    print("  • Levels for each person")
    print("  • Job titles and departments")
    print("  • Shows who has direct reports")

if __name__ == "__main__":
    main()
