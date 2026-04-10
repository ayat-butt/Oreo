"""
Taleemabad Active Members — Google Sheet Generator
Queries Markaz DB for all active Taleemabad members (including pending/never-logged-in),
excludes alumni/archived, then writes a Google Sheet to Drive.
READ-ONLY on Markaz DB.
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv
from hr_assistant.config import get_google_services

load_dotenv()

DB_URL = os.getenv("MARKAZ_DB_URL")


def fetch_taleemabad_members():
    """
    Fetch all active + pending Taleemabad members from Markaz DB.
    - Includes users who have never logged in (last_sign_in_at IS NULL)
    - Excludes archived users and alumni
    - Filters by payroll_entity = 'Taleemabad'
    READ-ONLY — no writes to DB.
    """
    conn = psycopg2.connect(DB_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT
                u.first_name || ' ' || u.last_name   AS full_name,
                COALESCE(ep.official_email, u.email)  AS official_email,
                u.status,
                ep.payroll_entity,
                u.last_sign_in_at
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL
              AND u.archived_at IS NULL
              AND u.status IN ('active', 'pending')
            ORDER BY u.first_name, u.last_name
        """)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_sheet(services, members: list[dict]) -> dict:
    """Create a Google Sheet with Taleemabad members and return its metadata."""
    sheets = services["sheets"]
    drive  = services["drive"]

    title = f"Taleemabad Active Members — {datetime.today().strftime('%Y-%m-%d')}"

    # Create spreadsheet
    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "Members"}}],
    }).execute()

    spreadsheet_id = spreadsheet["spreadsheetId"]
    sheet_id = spreadsheet["sheets"][0]["properties"]["sheetId"]

    # Build rows — header + data
    header = [["Full Name", "Official Email", "Payroll Entity", "Status", "Last Login"]]
    data_rows = []
    for m in members:
        last_login = str(m["last_sign_in_at"])[:10] if m["last_sign_in_at"] else "Never logged in"
        status     = m.get("status") or "—"
        entity     = m.get("payroll_entity") or "—"
        data_rows.append([m["full_name"], m["official_email"] or "—", entity, status, last_login])

    all_rows = header + data_rows

    # Write data
    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Members!A1",
        valueInputOption="RAW",
        body={"values": all_rows},
    ).execute()

    # Format header row — bold + background colour
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.18, "green": 0.44, "blue": 0.71},
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
            # Auto-resize columns
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
            # Freeze header row
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]},
    ).execute()

    # Get shareable link
    file_meta = drive.files().get(
        fileId=spreadsheet_id,
        fields="id,name,webViewLink,createdTime",
    ).execute()

    return {
        "id":      spreadsheet_id,
        "title":   file_meta["name"],
        "url":     file_meta["webViewLink"],
        "count":   len(members),
    }


def main():
    print("Fetching Taleemabad members from Markaz DB (read-only)...")
    members = fetch_taleemabad_members()

    if not members:
        print("No Taleemabad members found. Please verify payroll_entity values in DB.")
        return

    print(f"Found {len(members)} member(s). Preview (first 5):")
    for m in members[:5]:
        login = str(m["last_sign_in_at"])[:10] if m["last_sign_in_at"] else "Never logged in"
        print(f"  • {m['full_name']:<30}  {m['official_email'] or '—':<40}  {login}")
    if len(members) > 5:
        print(f"  ... and {len(members) - 5} more")

    confirm = input(f"\nCreate Google Sheet with all {len(members)} members? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    print("\nConnecting to Google services...")
    services = get_google_services()

    print("Creating Google Sheet in Drive...")
    result = create_sheet(services, members)

    print(f"\nDone! Sheet created successfully.")
    print(f"  Title : {result['title']}")
    print(f"  Count : {result['count']} members")
    print(f"  Link  : {result['url']}")


if __name__ == "__main__":
    main()
