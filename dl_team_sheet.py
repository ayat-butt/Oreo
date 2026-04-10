"""
Digital Learning Team — Full Hierarchy Sheet
Pulls all DL + Learning Engineering dept staff from Markaz,
groups them by sub-team lead, creates Google Sheet.
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
TEAL      = {"red": 0.05, "green": 0.45, "blue": 0.50}
WHITE     = {"red": 1.0,  "green": 1.0,  "blue": 1.0}
BLACK_BG  = {"red": 0.10, "green": 0.10, "blue": 0.10}

def _lighten(c, amt):
    return {k: min(v + amt, 1.0) for k, v in c.items()}


# ── Fetch ─────────────────────────────────────────────────────────────────────
def fetch_employees():
    conn = psycopg2.connect(DB_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT u.id,
                   u.first_name || ' ' || u.last_name AS full_name,
                   COALESCE(u.job_title, '-') AS job_title,
                   COALESCE(d.name, ep.department, '-') AS department,
                   ep.line_manager_id
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE u.deleted_at IS NULL AND u.archived_at IS NULL
            ORDER BY u.first_name, u.last_name
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


# ── Build hierarchy ────────────────────────────────────────────────────────────
def build(employees):
    by_id   = {e["id"]: e for e in employees}
    manages = defaultdict(list)
    for e in employees:
        mgr = e["line_manager_id"]
        if mgr and mgr in by_id:
            manages[mgr].append(e)
    return by_id, manages


def is_dl(person):
    d = (person["department"] or "").lower()
    return "digital learning" in d or "learning engineering" in d


# ── Sheet builder ─────────────────────────────────────────────────────────────
NCOLS = 5   # Level | Name | Department | Reports To | Role

def _fmt_req(shid, r0, r1, bg, bold=False, fg=None, size=10, italic=False):
    tf = {"bold": bold, "fontSize": size, "italic": italic}
    if fg:
        tf["foregroundColor"] = fg
    return {
        "repeatCell": {
            "range": {"sheetId": shid, "startRowIndex": r0, "endRowIndex": r1},
            "cell": {"userEnteredFormat": {"backgroundColor": bg, "textFormat": tf}},
            "fields": "userEnteredFormat(backgroundColor,textFormat)",
        }
    }


def create_sheet(services, amena, by_id, manages):
    sheets = services["sheets"]
    drive  = services["drive"]

    title = f"Digital Learning Team — Hierarchy ({datetime.today().strftime('%Y-%m-%d')})"
    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "DL Team"}}],
    }).execute()

    sid  = spreadsheet["spreadsheetId"]
    shid = spreadsheet["sheets"][0]["properties"]["sheetId"]

    rows = [["Level", "Name", "Department", "Reports To", "Job Title / Role"]]
    fmts = [_fmt_req(shid, 0, 1, BLACK_BG, bold=True, fg=WHITE, size=11)]
    ri   = 1

    def add(row, fmt=None):
        nonlocal ri
        rows.append(row)
        if fmt:
            fmts.append(fmt)
        ri += 1

    def mgr_name(person):
        mid = person["line_manager_id"]
        return by_id[mid]["full_name"] if mid and mid in by_id else "—"

    # ── MAIN LEAD ─────────────────────────────────────────────────────────────
    add(["Main Lead", amena["full_name"], amena["department"], "Ali Sipra (COO)", "Head of Digital Learning"],
        _fmt_req(shid, ri, ri+1, TEAL, bold=True, fg=WHITE, size=12))

    # ── Amena's direct reports ─────────────────────────────────────────────────
    amena_direct = sorted(manages[amena["id"]], key=lambda x: x["full_name"])
    for m in amena_direct:
        add(["  └ Direct Member", m["full_name"], m["department"], amena["full_name"], m["job_title"]],
            _fmt_req(shid, ri, ri+1, _lighten(TEAL, 0.45)))

    # Blank
    add(["", "", "", "", ""])

    # ── Sub-team leads (DL/LE dept, have reports, NOT directly under Amena) ───
    dl_leads = [
        e for e in by_id.values()
        if is_dl(e)
        and manages[e["id"]]
        and e["id"] != amena["id"]
    ]
    dl_leads.sort(key=lambda x: x["full_name"])

    # Section header
    add(["── SUB-TEAM LEADS & THEIR MEMBERS ──", "", "", "", ""],
        _fmt_req(shid, ri, ri+1, _lighten(TEAL, 0.20), bold=True, fg=WHITE, size=10))

    for lead in dl_leads:
        members = sorted(manages[lead["id"]], key=lambda x: x["full_name"])
        dl_members     = [m for m in members if is_dl(m)]
        non_dl_members = [m for m in members if not is_dl(m)]

        # Sub-lead row
        add(["Sub-Team Lead", lead["full_name"], lead["department"], mgr_name(lead), lead["job_title"]],
            _fmt_req(shid, ri, ri+1, _lighten(TEAL, 0.32), bold=True, size=10))

        # DL members
        for m in dl_members:
            add(["    └ Member", m["full_name"], m["department"], lead["full_name"], m["job_title"]],
                _fmt_req(shid, ri, ri+1, _lighten(TEAL, 0.55)))

        # Non-DL members (other depts embedded in this sub-team)
        for m in non_dl_members:
            add(["    └ (cross-dept)", m["full_name"], m["department"], lead["full_name"], m["job_title"]],
                _fmt_req(shid, ri, ri+1, {"red": 0.97, "green": 0.95, "blue": 0.88}))  # light yellow

        add(["", "", "", "", ""])

    # ── DL staff with no DL lead above them (embedded in non-DL teams) ────────
    # Collect all DL people already placed
    placed_ids = {amena["id"]}
    for m in manages[amena["id"]]:
        placed_ids.add(m["id"])
    for lead in dl_leads:
        placed_ids.add(lead["id"])
        for m in manages[lead["id"]]:
            placed_ids.add(m["id"])

    unplaced = [e for e in by_id.values() if is_dl(e) and e["id"] not in placed_ids]
    unplaced.sort(key=lambda x: x["full_name"])

    if unplaced:
        add(["── DL STAFF EMBEDDED IN OTHER TEAMS ──", "", "", "", ""],
            _fmt_req(shid, ri, ri+1, {"red": 0.55, "green": 0.55, "blue": 0.55},
                     bold=True, fg=WHITE, size=10))
        for e in unplaced:
            add(["  Member", e["full_name"], e["department"], mgr_name(e), e["job_title"]],
                _fmt_req(shid, ri, ri+1, {"red": 0.93, "green": 0.93, "blue": 0.93}))

    # ── Write ─────────────────────────────────────────────────────────────────
    sheets.spreadsheets().values().update(
        spreadsheetId=sid, range="DL Team!A1",
        valueInputOption="RAW", body={"values": rows},
    ).execute()

    # Column widths
    fmts += [
        {"updateDimensionProperties": {
            "range": {"sheetId": shid, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 220}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {
            "range": {"sheetId": shid, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2},
            "properties": {"pixelSize": 240}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {
            "range": {"sheetId": shid, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3},
            "properties": {"pixelSize": 180}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {
            "range": {"sheetId": shid, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4},
            "properties": {"pixelSize": 220}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {
            "range": {"sheetId": shid, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 5},
            "properties": {"pixelSize": 200}, "fields": "pixelSize"}},
        {"updateSheetProperties": {
            "properties": {"sheetId": shid, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount"}},
    ]

    sheets.spreadsheets().batchUpdate(spreadsheetId=sid, body={"requests": fmts}).execute()

    meta = drive.files().get(fileId=sid, fields="id,name,webViewLink").execute()
    return {"url": meta["webViewLink"], "rows": len(rows),
            "leads": len(dl_leads), "unplaced": len(unplaced)}


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Fetching DL team from Markaz (read-only)...")
    employees = fetch_employees()
    by_id, manages = build(employees)

    amena = next((e for e in employees if "Amena" in e["full_name"] and "Ahmed" in e["full_name"]), None)
    if not amena:
        print("ERROR: Amena Ahmed not found in Markaz.")
        return

    dl_leads = [e for e in employees if is_dl(e) and manages[e["id"]] and e["id"] != amena["id"]]
    print(f"\n  Main Lead : Amena Ahmed")
    print(f"  Direct reports: {[m['full_name'] for m in manages[amena['id']]]}")
    print(f"\n  Sub-team leads ({len(dl_leads)}):")
    for lead in sorted(dl_leads, key=lambda x: x["full_name"]):
        members = manages[lead["id"]]
        print(f"    > {lead['full_name']} ({lead['department']}) -> {len(members)} member(s)")
        for m in sorted(members, key=lambda x: x["full_name"]):
            print(f"        - {m['full_name']} ({m['department']})")

    confirm = input("\nCreate Google Sheet? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    print("\nConnecting to Google...")
    services = get_google_services()
    result = create_sheet(services, amena, by_id, manages)

    print(f"\nDone!")
    print(f"  Rows     : {result['rows']}")
    print(f"  Sub-leads: {result['leads']}")
    print(f"  Link     : {result['url']}")

if __name__ == "__main__":
    main()
