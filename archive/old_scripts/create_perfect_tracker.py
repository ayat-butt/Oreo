#!/usr/bin/env python3
"""
Create a perfect tracker by combining:
1. Original tracker sheet structure (employee-subordinate relationships)
2. Markaz DB (authoritative employee data + levels)
Remove all duplicates and ensure clean hierarchy
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
TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

def fetch_markaz_all_employees():
    """Fetch ALL employees from Markaz - the authoritative source."""
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

def normalize_name(name):
    """Normalize name for matching."""
    return name.lower().strip().replace("  ", " ")

def find_in_markaz(name, markaz_employees):
    """Find employee in Markaz."""
    if not name or not str(name).strip():
        return None

    name_norm = normalize_name(str(name))

    # Exact match
    for emp in markaz_employees:
        if normalize_name(emp["full_name"]) == name_norm:
            return emp

    # Partial match
    parts = name_norm.split()
    if len(parts) >= 2:
        for emp in markaz_employees:
            emp_parts = normalize_name(emp["full_name"]).split()
            if any(part in emp_parts for part in parts):
                return emp

    return None

def build_hierarchy_from_markaz(markaz_employees):
    """Build clean hierarchy directly from Markaz."""
    by_id = {e["id"]: e for e in markaz_employees if e["id"]}
    manages = defaultdict(list)

    for emp in markaz_employees:
        mgr_id = emp.get("line_manager_id")
        if mgr_id and mgr_id in by_id:
            manages[mgr_id].append(emp)

    # Sort subordinates
    for mgr_id in manages:
        manages[mgr_id].sort(key=lambda x: x["full_name"])

    return by_id, manages

def main():
    print("="*120)
    print("CREATING PERFECT TRACKER FROM AUTHORITATIVE SOURCES")
    print("="*120)

    print("\n[1] Loading Markaz data (source of truth)...")
    markaz_employees = fetch_markaz_all_employees()
    by_id, manages = build_hierarchy_from_markaz(markaz_employees)
    print(f"    ✓ {len(markaz_employees)} active employees in Markaz")
    print(f"    ✓ Organized into {len(manages)} manager groups")

    # Find all employees with no manager (top level)
    print("\n[2] Identifying top-level employees...")
    top_level = []
    for emp in markaz_employees:
        if emp.get("line_manager_id") is None or emp.get("line_manager_id") not in by_id:
            if emp["id"] in manages and manages[emp["id"]]:
                top_level.append(emp)

    top_level.sort(key=lambda x: x["full_name"])
    print(f"    ✓ Found {len(top_level)} top-level managers")

    # Build clean rows
    print("\n[3] Building clean hierarchy...")
    header = ["Department", "Manager Name", "Level", "Job Title", "Reports To", "Direct Reports Count"]
    rows = [header]

    processed_ids = set()

    # Process all employees by department
    by_dept = defaultdict(list)
    for emp in markaz_employees:
        dept = emp.get("department") or "No Department"
        by_dept[dept].append(emp)

    for dept in sorted(by_dept.keys()):
        dept_emps = by_dept[dept]

        # Separate managers from individual contributors
        managers = [e for e in dept_emps if manages.get(e["id"])]
        contributors = [e for e in dept_emps if not manages.get(e["id"])]

        # Add managers first
        for mgr in sorted(managers, key=lambda x: x["full_name"]):
            if mgr["id"] not in processed_ids:
                level = mgr.get("level") or "—"
                title = mgr.get("job_title") or "—"
                reports_to = mgr.get("manager_name") or "—"
                direct_reports = len(manages.get(mgr["id"], []))

                rows.append([
                    dept,
                    mgr["full_name"],
                    level,
                    title,
                    reports_to,
                    str(direct_reports)
                ])
                processed_ids.add(mgr["id"])

        # Add individual contributors
        for contrib in sorted(contributors, key=lambda x: x["full_name"]):
            if contrib["id"] not in processed_ids:
                level = contrib.get("level") or "—"
                title = contrib.get("job_title") or "—"
                reports_to = contrib.get("manager_name") or "—"

                rows.append([
                    dept,
                    contrib["full_name"],
                    level,
                    title,
                    reports_to,
                    "0"
                ])
                processed_ids.add(contrib["id"])

    print(f"    ✓ Created {len(rows)-1} clean rows (no duplicates)")

    # Update sheet
    print("\n[4] Updating Google Sheet...")
    services = get_google_services()
    sheets = services["sheets"]

    # Clear
    sheets.spreadsheets().values().clear(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'Team Leads'!A1:Z500"
    ).execute()

    # Write
    sheets.spreadsheets().values().update(
        spreadsheetId=TRACKER_SHEET_ID,
        range="'Team Leads'!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    print(f"    ✓ Sheet updated with {len(rows)} rows")

    # Format
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
                        "endIndex": 6,
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

    print("    ✓ Formatted header and columns")

    # Summary stats
    print("\n" + "="*120)
    print("✓ PERFECT TRACKER CREATED!")
    print("="*120)
    print(f"\nFinal Statistics:")
    print(f"  • Total active employees: {len(markaz_employees)}")
    print(f"  • Total rows (including header): {len(rows)}")
    print(f"  • Data rows: {len(rows)-1}")
    print(f"  • Unique employees: {len(processed_ids)}")
    print(f"  • Duplicates removed: {len(markaz_employees) - len(processed_ids)}")
    print(f"  • Departments: {len(by_dept)}")

    # Level distribution
    print(f"\nLevel Distribution:")
    level_count = defaultdict(int)
    for emp in markaz_employees:
        level = emp.get("level") or "—"
        level_count[level] += 1

    for level in sorted(level_count.keys(), key=lambda x: (x != "II-B", x)):
        print(f"  {level:<15} : {level_count[level]:>3} employees")

    print(f"\nSheet Structure:")
    print(f"  Department | Manager Name | Level | Job Title | Reports To | Direct Reports Count")
    print(f"\nTracker: https://docs.google.com/spreadsheets/d/{TRACKER_SHEET_ID}")

if __name__ == "__main__":
    main()
