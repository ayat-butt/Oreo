"""
Org Chart — Team Leads & Subordinates Google Sheet Generator
Reads Markaz DB (read-only) to build line-manager hierarchy,
then creates a Google Sheet with each team lead and their members.
"""

import os
import sys
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv
from hr_assistant.config import get_google_services

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

DB_URL = os.getenv("MARKAZ_DB_URL")

# Colour palette
COLOURS = [
    {"red": 0.18, "green": 0.44, "blue": 0.71},   # blue
    {"red": 0.13, "green": 0.55, "blue": 0.13},   # green
    {"red": 0.60, "green": 0.20, "blue": 0.60},   # purple
    {"red": 0.80, "green": 0.40, "blue": 0.00},   # orange
    {"red": 0.20, "green": 0.60, "blue": 0.60},   # teal
    {"red": 0.70, "green": 0.10, "blue": 0.10},   # red
    {"red": 0.40, "green": 0.40, "blue": 0.00},   # olive
]


# ── Data fetch ────────────────────────────────────────────────────────────────

def fetch_org_data():
    """Pull all active employees with line-manager relationship from Markaz DB."""
    conn = psycopg2.connect(DB_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT
                u.id,
                u.first_name || ' ' || u.last_name  AS full_name,
                COALESCE(u.job_title, '—')           AS job_title,
                COALESCE(d.name, ep.department, '—') AS department,
                ep.line_manager_id
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            LEFT JOIN departments d        ON u.department_id = d.id
            WHERE u.deleted_at  IS NULL
              AND u.archived_at IS NULL
              AND u.status IN ('active', 'pending')
            ORDER BY u.first_name, u.last_name
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def build_hierarchy(employees: list[dict]):
    """
    Returns:
        team_leads  — list of dicts for people who have at least one direct report
        subordinates — dict {manager_id: [employee_dict, ...]}
        no_manager  — list of employees with no manager and no subordinates
    """
    by_id = {e["id"]: e for e in employees}
    subordinates: dict = {}
    managed_ids = set()

    for emp in employees:
        mgr_id = emp["line_manager_id"]
        if mgr_id and mgr_id in by_id:
            subordinates.setdefault(mgr_id, []).append(emp)
            managed_ids.add(mgr_id)

    team_leads = [by_id[mid] for mid in managed_ids]
    team_leads.sort(key=lambda x: x["full_name"])

    # Employees with no manager and not a manager themselves
    all_managed = {e["id"] for leads in subordinates.values() for e in leads}
    no_manager = [
        e for e in employees
        if e["id"] not in managed_ids and e["id"] not in all_managed
    ]

    return team_leads, subordinates, no_manager


# ── Sheet builder ─────────────────────────────────────────────────────────────

def create_sheet(services, team_leads, subordinates, no_manager) -> dict:
    sheets = services["sheets"]
    drive  = services["drive"]

    title = f"Org Chart — Team Leads & Members ({datetime.today().strftime('%Y-%m-%d')})"

    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "Org Chart"}}],
    }).execute()

    spreadsheet_id = spreadsheet["spreadsheetId"]
    sheet_id       = spreadsheet["sheets"][0]["properties"]["sheetId"]

    # ── Build rows ──────────────────────────────────────────────────────────
    rows = [["Team Lead", "Title", "Member Name", "Member Title", "Department"]]
    formatting_requests = []
    row_idx = 1   # 0-based; row 0 = header

    # Track which rows are team-lead headers so we can colour them
    lead_rows = []   # list of (row_index_0based, colour_dict)

    for i, lead in enumerate(team_leads):
        colour = COLOURS[i % len(COLOURS)]
        members = subordinates.get(lead["id"], [])

        # Team-lead row (first member on same row for compactness)
        first = members[0] if members else None
        rows.append([
            lead["full_name"],
            lead["job_title"],
            first["full_name"]  if first else "",
            first["job_title"]  if first else "",
            first["department"] if first else "",
        ])
        lead_rows.append((row_idx, colour))
        row_idx += 1

        # Remaining members — leave Team Lead columns blank
        for mem in members[1:]:
            rows.append(["", "", mem["full_name"], mem["job_title"], mem["department"]])
            row_idx += 1

        # Blank separator row between teams
        rows.append(["", "", "", "", ""])
        row_idx += 1

    # Unassigned section
    if no_manager:
        rows.append(["— No manager assigned —", "", "", "", ""])
        lead_rows.append((row_idx, {"red": 0.5, "green": 0.5, "blue": 0.5}))
        row_idx += 1
        for emp in no_manager:
            rows.append(["", "", emp["full_name"], emp["job_title"], emp["department"]])
            row_idx += 1

    # ── Write data ──────────────────────────────────────────────────────────
    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Org Chart!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    # ── Format: header row ──────────────────────────────────────────────────
    formatting_requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.1, "green": 0.1, "blue": 0.1},
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
    })

    # ── Format: team-lead rows (coloured background + bold) ─────────────────
    for (ridx, colour) in lead_rows:
        formatting_requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": ridx,
                    "endRowIndex": ridx + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": colour,
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                        },
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        })

    # ── Auto-resize + freeze header ─────────────────────────────────────────
    formatting_requests += [
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 5,
                }
            }
        },
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 1},
                },
                "fields": "gridProperties.frozenRowCount",
            }
        },
    ]

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": formatting_requests},
    ).execute()

    file_meta = drive.files().get(
        fileId=spreadsheet_id,
        fields="id,name,webViewLink",
    ).execute()

    return {
        "id":    spreadsheet_id,
        "title": file_meta["name"],
        "url":   file_meta["webViewLink"],
        "leads": len(team_leads),
        "total": sum(len(v) for v in subordinates.values()),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Fetching org data from Markaz DB (read-only)…")
    employees = fetch_org_data()
    print(f"  {len(employees)} active employees found.")

    team_leads, subordinates, no_manager = build_hierarchy(employees)

    print(f"\n  {len(team_leads)} team lead(s) identified:\n")
    for lead in team_leads:
        members = subordinates.get(lead["id"], [])
        print(f"  > {lead['full_name']} ({lead['job_title']}) - {len(members)} member(s)")
        for m in members:
            print(f"      - {m['full_name']} - {m['job_title']}")

    if no_manager:
        print(f"\n  {len(no_manager)} employee(s) with no manager assigned:")
        for e in no_manager:
            print(f"    • {e['full_name']} — {e['job_title']}")

    confirm = input(
        f"\nCreate Google Sheet with {len(team_leads)} teams? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Cancelled.")
        return

    print("\nConnecting to Google services…")
    services = get_google_services()

    print("Creating Google Sheet…")
    result = create_sheet(services, team_leads, subordinates, no_manager)

    print(f"\nDone!")
    print(f"  Title  : {result['title']}")
    print(f"  Leads  : {result['leads']}")
    print(f"  Members: {result['total']}")
    print(f"  Link   : {result['url']}")


if __name__ == "__main__":
    main()
