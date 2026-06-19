#!/usr/bin/env python3
"""
Fetch employee levels from Markaz DB and add them to the hierarchy tracker sheet.
Cross-checks tracker sheet with Markaz data for accuracy.
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
SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
GID = "654305400"

def fetch_levels_from_markaz():
    """Fetch employee levels from Markaz DB."""
    conn = psycopg2.connect(DB_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT
                u.id,
                u.first_name || ' ' || u.last_name AS full_name,
                ep.level,
                ep.job_title,
                ep.line_manager_id
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL AND u.archived_at IS NULL
            ORDER BY u.first_name, u.last_name
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def main():
    print("Step 1: Fetching Markaz data...")
    employees = fetch_levels_from_markaz()
    print(f"  Found {len(employees)} employees in Markaz")

    # Create a lookup map
    by_name = {}
    for emp in employees:
        name = emp["full_name"].lower().strip()
        by_name[name] = emp

    print("\nStep 2: Reading tracker sheet...")
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
        range=f"'{sheet_name}'!A1:Z200"
    ).execute()

    rows = result.get("values", [])
    print(f"  Found {len(rows)} rows in tracker sheet")

    # Show sample of levels found
    print("\nStep 3: Sample of levels in Markaz:")
    sample_levels = {}
    for emp in employees[:30]:
        level = emp.get("level") or "—"
        if level not in sample_levels:
            sample_levels[level] = []
        if len(sample_levels[level]) < 3:
            sample_levels[level].append(emp["full_name"])

    for level, names in sample_levels.items():
        print(f"  {level}: {', '.join(names)}")

    # Cross-check tracker names with Markaz
    print("\nStep 4: Cross-checking tracker with Markaz...")
    header = rows[0]
    found_count = 0
    missing_count = 0
    missing_names = []

    for row_idx, row in enumerate(rows[1:], start=2):
        # Extract names from this row
        team_lead = row[2] if len(row) > 2 else ""
        reports_to = row[3] if len(row) > 3 else ""
        team_members = row[4] if len(row) > 4 else ""

        names_to_check = []
        if team_lead:
            names_to_check.append(team_lead.strip())
        if reports_to:
            names_to_check.append(reports_to.strip())
        if team_members:
            for name in team_members.split(","):
                names_to_check.append(name.strip())

        for name in names_to_check:
            if not name or name.startswith("#"):
                continue

            name_lower = name.lower()
            if name_lower in by_name:
                found_count += 1
            else:
                missing_count += 1
                if name not in missing_names:
                    missing_names.append(name)

    print(f"  Found in Markaz: {found_count}")
    print(f"  NOT found in Markaz: {missing_count}")

    if missing_names[:10]:
        print(f"\n  Sample of missing names (first 10):")
        for name in missing_names[:10]:
            print(f"    - {name}")
        if len(missing_names) > 10:
            print(f"    ... and {len(missing_names) - 10} more")

    # Show the levels we can add
    print("\n" + "="*100)
    print("RECOMMENDATION:")
    print("="*100)
    print(f"\nYour tracker sheet has {len(rows)-1} rows.")
    print(f"Markaz DB has {len(employees)} active employees with job levels.")
    print(f"\nTo add levels to the hierarchy tracker:")
    print("  1. I can add a 'Level' column (after 'Reports To')")
    print("  2. Look up each person in Markaz and fill in their job_level")
    print("  3. Flag any names not found in Markaz for manual review")
    print("\nWould you like me to:")
    print("  A) Add Level column and populate from Markaz")
    print("  B) Show a preview of 10 rows with levels added")
    print("  C) Export employee data + levels to CSV first for review")

if __name__ == "__main__":
    main()
