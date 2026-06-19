#!/usr/bin/env python3
"""
Create a comprehensive hierarchy sheet organized by department.
Shows all employees with clear team structure.
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

def group_by_department(employees):
    """Group employees by department."""
    by_dept = defaultdict(list)
    for emp in employees:
        dept = emp.get("department") or "No Department"
        by_dept[dept].append(emp)
    return dict(sorted(by_dept.items()))

def build_team_tree(manager, employees_by_id, manages):
    """Build a tree for a team lead and their subordinates."""
    rows = []

    def add_node(emp, indent_level=0):
        indent = "  " * indent_level
        level = emp.get("level") or "—"
        mgr = emp.get("manager_name") or "—"
        title = emp.get("job_title") or "—"

        rows.append([
            indent + emp["full_name"],
            level,
            title,
            mgr,
            str(len(manages.get(emp["id"], [])))
        ])

        # Add subordinates
        for sub in sorted(manages.get(emp["id"], []), key=lambda x: x["full_name"]):
            add_node(sub, indent_level + 1)

    add_node(manager)
    return rows

def create_full_hierarchy_sheet(services, employees):
    """Create a comprehensive hierarchy sheet by department."""
    sheets = services["sheets"]
    drive = services["drive"]

    # Build lookup structures
    by_id = {e["id"]: e for e in employees if e["id"]}
    manages = defaultdict(list)
    for emp in employees:
        mgr_id = emp.get("line_manager_id")
        if mgr_id and mgr_id in by_id:
            manages[mgr_id].append(emp)

    # Group by department
    by_dept = group_by_department(employees)

    title = f"Summit Full Hierarchy — By Department ({datetime.today().strftime('%Y-%m-%d')})"

    # Create new spreadsheet
    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "Full Org"}}],
    }).execute()

    sid = spreadsheet["spreadsheetId"]
    shid = spreadsheet["sheets"][0]["properties"]["sheetId"]

    # Build header
    header = ["Name (Team Lead → Team Members)", "Level", "Job Title", "Manager", "Direct Reports"]

    # Build data rows - organize by department
    all_rows = [header]

    for dept, dept_employees in by_dept.items():
        # Department header
        all_rows.append([f"═══ {dept} ═══", "", "", "", ""])

        # Find team leads in this department (those with direct reports)
        team_leads = []
        individual_contributors = []

        for emp in dept_employees:
            if manages.get(emp["id"]):
                team_leads.append(emp)
            else:
                individual_contributors.append(emp)

        # Add team leads and their teams first
        for lead in sorted(team_leads, key=lambda x: x["full_name"]):
            team_rows = build_team_tree(lead, by_id, manages)
            all_rows.extend(team_rows)

        # Add individual contributors
        for ic in sorted(individual_contributors, key=lambda x: x["full_name"]):
            level = ic.get("level") or "—"
            title = ic.get("job_title") or "—"
            mgr = ic.get("manager_name") or "—"
            all_rows.append([
                "  " + ic["full_name"],
                level,
                title,
                mgr,
                "0"
            ])

        # Separator
        all_rows.append(["", "", "", "", ""])

    # Write to sheet
    sheets.spreadsheets().values().update(
        spreadsheetId=sid,
        range="'Full Org'!A1",
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
                        "endIndex": 5,
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
    print("Creating comprehensive hierarchy sheet...\n")

    print("[1] Fetching org data from Markaz...")
    employees = fetch_org_data()
    print(f"    ✓ {len(employees)} employees")

    print("\n[2] Organizing by department and team...")
    by_dept = group_by_department(employees)
    print(f"    ✓ {len(by_dept)} departments")

    print("\n[3] Connecting to Google...")
    services = get_google_services()

    print("\n[4] Creating comprehensive sheet...")
    result = create_full_hierarchy_sheet(services, employees)

    print("\n" + "="*100)
    print("✓ FULL HIERARCHY SHEET CREATED!")
    print("="*100)
    print(f"\nTitle: {result['title']}")
    print(f"Rows:  {result['rows']}")
    print(f"Link:  {result['url']}")
    print("\nStructure:")
    print("  === Department ===")
    print("    Team Lead")
    print("      └─ Subordinate 1")
    print("      └─ Subordinate 2")
    print("    Individual Contributor")
    print("\nEach person shows:")
    print("  • Name (indented if they're a subordinate)")
    print("  • Level (II-B, II-A, I-A, I-B, etc.)")
    print("  • Job Title")
    print("  • Manager Name")
    print("  • Count of Direct Reports")

if __name__ == "__main__":
    main()
