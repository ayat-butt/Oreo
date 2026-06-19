"""
Main Team Leads Sheet — pulled live from Markaz DB.
Shows every team lead (anyone with direct reports) organised by
their parent department (who they ultimately roll up to under the CEO).
READ-ONLY on Markaz.
"""

import sys, os
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
load_dotenv()

import psycopg2, psycopg2.extras
from hr_assistant.config import get_google_services

DB_URL = os.getenv("MARKAZ_DB_URL")

# ── Colours ───────────────────────────────────────────────────────────────────
WHITE = {"red": 1, "green": 1, "blue": 1}

DEPT_COLOURS = {
    "COO / Programs":       {"red": 0.62, "green": 0.35, "blue": 0.30},   # salmon
    "COO / Growth":         {"red": 0.45, "green": 0.62, "blue": 0.35},   # green
    "COO / Digital Learning": {"red": 0.35, "green": 0.50, "blue": 0.65}, # blue-grey
    "CTO / Tech":           {"red": 0.20, "green": 0.45, "blue": 0.20},   # dark green
    "CSO":                  {"red": 0.20, "green": 0.40, "blue": 0.65},   # blue
    "Operations":           {"red": 0.55, "green": 0.35, "blue": 0.60},   # purple
    "HR":                   {"red": 0.70, "green": 0.45, "blue": 0.20},   # orange
    "Finance":              {"red": 0.30, "green": 0.50, "blue": 0.50},   # teal
}
HEADER_BG = {"red": 0.10, "green": 0.10, "blue": 0.10}


def _lighten(c, amt):
    return {k: min(v + amt, 1.0) for k, v in c.items()}


# ── Fetch org data from Markaz ────────────────────────────────────────────────

def fetch_employees():
    conn = psycopg2.connect(DB_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT
                u.id,
                u.first_name || ' ' || u.last_name AS full_name,
                ep.line_manager_id
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL AND u.archived_at IS NULL
            ORDER BY u.first_name, u.last_name
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


# ── Build hierarchy ───────────────────────────────────────────────────────────

def build_tree(employees):
    by_id   = {e["id"]: e for e in employees}
    manages = defaultdict(list)
    for e in employees:
        mgr = e["line_manager_id"]
        if mgr and mgr in by_id:
            manages[mgr].append(e)
    return by_id, manages


def find_person(by_id, first, last=""):
    for e in by_id.values():
        n = e["full_name"].lower()
        if first.lower() in n and (not last or last.lower() in n):
            return e
    return None


# ── Department sections — each is a top-level lead ID + label ────────────────
# We'll walk the tree from each known top-level lead.

def collect_leads(manages, root_id, depth=0, max_depth=4):
    """Recursively collect all leads (people with direct reports) under root."""
    result = []
    for sub in manages.get(root_id, []):
        if manages[sub["id"]]:   # sub has reports → is a lead
            result.append((sub, depth, manages[sub["id"]]))
        result += collect_leads(manages, sub["id"], depth + 1, max_depth)
    return result


# ── Sheet builder ─────────────────────────────────────────────────────────────

NCOLS = 5   # Department | Team Lead | Reports To | Member Name | Note

def create_sheet(services, sections) -> dict:
    sheets = services["sheets"]
    drive  = services["drive"]

    title = f"Main Team Leads — Markaz ({datetime.today().strftime('%Y-%m-%d')})"

    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "Team Leads"}}],
    }).execute()

    sid = spreadsheet["spreadsheetId"]
    shid = spreadsheet["sheets"][0]["properties"]["sheetId"]

    rows = [["Department", "Team Lead", "Reports To", "Team Member", "# Members"]]
    fmts = [{
        "repeatCell": {
            "range": {"sheetId": shid, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {
                "backgroundColor": HEADER_BG,
                "textFormat": {"bold": True, "foregroundColor": WHITE, "fontSize": 11},
                "horizontalAlignment": "CENTER",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
        }
    }]
    ri = 1

    for dept_label, leads, by_id, manages in sections:
        colour = DEPT_COLOURS.get(dept_label, {"red": 0.5, "green": 0.5, "blue": 0.5})

        # ── Section header row ───────────────────────────────────────────
        rows.append([dept_label, "", "", "", ""])
        fmts.append({
            "repeatCell": {
                "range": {"sheetId": shid, "startRowIndex": ri, "endRowIndex": ri + 1},
                "cell": {"userEnteredFormat": {
                    "backgroundColor": colour,
                    "textFormat": {"bold": True, "foregroundColor": WHITE, "fontSize": 11},
                }},
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        })
        ri += 1

        # ── One row per team lead ────────────────────────────────────────
        for lead, depth, members in leads:
            mgr_id   = lead["line_manager_id"]
            mgr_name = by_id[mgr_id]["full_name"] if mgr_id and mgr_id in by_id else "—"
            member_names = ", ".join(m["full_name"] for m in sorted(members, key=lambda x: x["full_name"]))
            rows.append([
                "",
                lead["full_name"],
                mgr_name,
                member_names,
                str(len(members)),
            ])

            lead_colour = _lighten(colour, 0.35 + depth * 0.08)
            fmts.append({
                "repeatCell": {
                    "range": {"sheetId": shid, "startRowIndex": ri, "endRowIndex": ri + 1},
                    "cell": {"userEnteredFormat": {
                        "backgroundColor": lead_colour,
                        "textFormat": {"bold": True, "fontSize": 10},
                    }},
                    "fields": "userEnteredFormat(backgroundColor,textFormat)",
                }
            })
            ri += 1

        # Blank separator
        rows.append(["", "", "", "", ""])
        ri += 1

    # Write
    sheets.spreadsheets().values().update(
        spreadsheetId=sid, range="Team Leads!A1",
        valueInputOption="RAW", body={"values": rows},
    ).execute()

    # Auto-resize + freeze + wrap member column
    fmts += [
        {
            "autoResizeDimensions": {
                "dimensions": {"sheetId": shid, "dimension": "COLUMNS",
                               "startIndex": 0, "endIndex": NCOLS}
            }
        },
        {
            "updateSheetProperties": {
                "properties": {"sheetId": shid, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": shid, "startRowIndex": 0,
                          "endRowIndex": len(rows), "startColumnIndex": 3, "endColumnIndex": 4},
                "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP"}},
                "fields": "userEnteredFormat(wrapStrategy)",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {"sheetId": shid, "dimension": "COLUMNS",
                          "startIndex": 3, "endIndex": 4},
                "properties": {"pixelSize": 420},
                "fields": "pixelSize",
            }
        },
    ]

    sheets.spreadsheets().batchUpdate(spreadsheetId=sid, body={"requests": fmts}).execute()

    meta = drive.files().get(fileId=sid, fields="id,name,webViewLink").execute()
    return {"id": sid, "title": meta["name"], "url": meta["webViewLink"], "rows": len(rows)}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Fetching org data from Markaz (read-only)...")
    employees = fetch_employees()
    by_id, manages = build_tree(employees)

    print(f"  {len(employees)} employees loaded.")

    # Identify anchors
    haroon  = find_person(by_id, "Haroon", "Yasin")
    zeshan  = find_person(by_id, "Zeshan", "Ali")
    saad    = find_person(by_id, "Saad",   "Zahid")

    ali_sipra = find_person(by_id, "Ali", "Sipra")
    mashhood  = find_person(by_id, "Mashhood")
    bilal     = find_person(by_id, "Bilal", "Sadiq")
    waqas     = find_person(by_id, "Waqas", "Tanveer")
    amena     = find_person(by_id, "Amena", "Ahmed")
    fahad     = find_person(by_id, "Fahad", "Rao")
    sabeena   = find_person(by_id, "Sabeena")

    def leads_under(root):
        return collect_leads(manages, root["id"]) if root else []

    # Build sections: (label, [(lead, depth, members)], by_id, manages)
    sections = [
        ("COO / Programs",          leads_under(bilal),   by_id, manages),
        ("COO / Growth",            leads_under(waqas),   by_id, manages),
        ("COO / Digital Learning",  leads_under(amena),   by_id, manages),
        ("CTO / Tech",              leads_under(mashhood),by_id, manages),
        ("CSO",                     leads_under(fahad),   by_id, manages),
        ("Operations",              leads_under(sabeena), by_id, manages),
        ("HR",                      leads_under(zeshan),  by_id, manages),
        ("Finance",                 leads_under(saad),    by_id, manages),
    ]

    total = 0
    for label, leads, *_ in sections:
        print(f"\n  [{label}] — {len(leads)} lead(s)")
        for lead, depth, members in leads:
            indent = "  " * (depth + 2)
            print(f"{indent}{lead['full_name']} → {len(members)} members")
        total += len(leads)

    print(f"\n  Total main leads: {total}")

    confirm = input("\nCreate Google Sheet? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    print("\nConnecting to Google...")
    services = get_google_services()
    result = create_sheet(services, sections)

    print(f"\nDone!")
    print(f"  Title : {result['title']}")
    print(f"  Rows  : {result['rows']}")
    print(f"  Link  : {result['url']}")


if __name__ == "__main__":
    main()
