"""
Org Chart — built from Canva organogram (screenshots, April 2026).
Hierarchical layout: Section → Team Lead → Sub-Team → Sub-Lead → Member
Column structure mirrors hierarchy depth visually.
READ-ONLY on Markaz. Writes to Google Sheets/Drive only.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from datetime import datetime
from hr_assistant.config import get_google_services

# ── Org data ──────────────────────────────────────────────────────────────────
# Each entry:  section, color_key, lead, direct_members, sub_teams
# sub_teams:   name, lead, sub_teams (nested, same structure), members

ORG = [

    # ══ C-SUITE ════════════════════════════════════════════════════════════════
    {
        "section":        "C-Suite",
        "color_key":      "black",
        "lead":           {"name": "Haroon Yasin", "role": "CEO"},
        "direct_members": [
            {"name": "Ali Sipra",            "role": "COO"},
            {"name": "Mashhood Ali Rastgar", "role": "CTO"},
            {"name": "Sabeena Abbasi",       "role": "VP / Operations"},
            {"name": "Zuhaib Sheikh",        "role": "Fractional CPO"},
            {"name": "Fahad Rao",            "role": "CSO"},
        ],
        "sub_teams": [],
    },

    # ══ PROGRAMS — ISLAMABAD REGION ════════════════════════════════════════════
    {
        "section":        "Programs — Islamabad Region",
        "color_key":      "salmon",
        "lead":           {"name": "Muhammad Bilal Sadiq", "role": "PM (ICT)"},
        "direct_members": [
            {"name": "Momina Raja",                     "role": "Primary Teacher Training + Extension"},
            {"name": "Abdul Waheed",                    "role": "Coach / Head Teachers Training"},
            {"name": "Hasnat Tariq",                    "role": "Data+ Dashboard — UB-I"},
            {"name": "Sara Fatima",                     "role": "CRO — Nilor"},
            {"name": "Chaudhary Hashir Hussain Shahid", "role": "Sihala"},
        ],
        "sub_teams": [
            {
                "name":    "UB-II — Middle & High",
                "lead":    {"name": "Anam Masood", "role": "UB-II (Middle & High)"},
                "members": [
                    {"name": "Muhammad Haris", "role": "Data"},
                ],
                "sub_teams": [],
            },
        ],
    },

    # ══ PROGRAMS — BALOCHISTAN REGION ══════════════════════════════════════════
    {
        "section":        "Programs — Balochistan Region",
        "color_key":      "salmon",
        "lead":           {"name": "Abdullah Durrani", "role": "PM (Balochistan)"},
        "direct_members": [
            {"name": "Haya Abid", "role": "Product"},
            {"name": "Coaches",   "role": "Field Coaches (unnamed)"},
        ],
        "sub_teams": [],
    },

    # ══ PROGRAMS — RAWALPINDI REGION ═══════════════════════════════════════════
    {
        "section":        "Programs — Rawalpindi Region",
        "color_key":      "salmon",
        "lead":           {"name": "Summaya Shakur", "role": "PM (RWP)"},
        "direct_members": [
            {"name": "Coaches", "role": "Field Coaches (unnamed)"},
        ],
        "sub_teams": [
            {
                "name":    "Growth Sub-Team",
                "lead":    {"name": "Shayan Ahmad", "role": "Growth"},
                "members": [
                    {"name": "Muqadas Saleem",  "role": "DL"},
                    {"name": "Abdul Rehman",    "role": "Data"},
                    {"name": "Tayyaba Hamna",   "role": "DL"},
                    {"name": "Noor Faiz Malik", "role": "Product"},
                ],
                "sub_teams": [],
            },
        ],
    },

    # ══ PROGRAMS — PUNJAB REGION (PEF) ════════════════════════════════════════
    {
        "section":        "Programs — Punjab Region (PEF)",
        "color_key":      "salmon",
        "lead":           {"name": "Ahmed Javed", "role": "PM (PEF / Punjab)"},
        "direct_members": [],
        "sub_teams": [
            {
                "name":    "PEF Field Team",
                "lead":    {"name": "Gul Perwasha Cheema", "role": "Team Lead"},
                "members": [
                    {"name": "Danish Iqbal",  "role": "Product"},
                    {"name": "Muhammad Saim", "role": "Eng"},
                ],
                "sub_teams": [
                    {
                        "name":    "DL Sub-Team",
                        "lead":    {"name": "Mahrah Ashraf", "role": "DL"},
                        "members": [
                            {"name": "Hareem Fatima", "role": "DL"},
                        ],
                        "sub_teams": [],
                    },
                ],
            },
        ],
    },

    # ══ DIGITAL LEARNING (DL) ══════════════════════════════════════════════════
    {
        "section":        "Digital Learning (DL)",
        "color_key":      "grey",
        "lead":           {"name": "Amena Ahmed", "role": "Head of DL"},
        "direct_members": [],
        "sub_teams": [
            {
                "name":    "Schema Development",
                "lead":    {"name": "Sheikh Nimra Rasheed", "role": "Eng"},
                "members": [
                    {"name": "Momna Tariq", "role": "DL"},
                ],
                "sub_teams": [],
            },
        ],
    },

    # ══ GROWTH — SINDH ═════════════════════════════════════════════════════════
    {
        "section":        "Growth — Sindh",
        "color_key":      "grey",
        "lead":           {"name": "Waqas Tanveer", "role": "Head of Growth"},
        "direct_members": [
            {"name": "Shayan Ahmad", "role": "Growth — Sindh"},
        ],
        "sub_teams": [],
    },

    # ══ GROWTH — INTERNATIONAL ════════════════════════════════════════════════
    {
        "section":        "Growth — International",
        "color_key":      "grey",
        "lead":           {"name": "Waqas Tanveer", "role": "Head of Growth"},
        "direct_members": [
            {"name": "Syed Junaid Ali Zaidi", "role": ""},
            {"name": "Mahnoor Tanweer",        "role": ""},
        ],
        "sub_teams": [],
    },

    # ══ TECH — USER MANAGEMENT ════════════════════════════════════════════════
    {
        "section":        "Tech — User Management",
        "color_key":      "green",
        "lead":           {"name": "Muhammad Kamal", "role": "Eng"},
        "direct_members": [
            {"name": "Mah Noor",      "role": "Eng"},
            {"name": "Shoaib Ud Din", "role": "Eng"},
        ],
        "sub_teams": [],
    },

    # ══ TECH — EG ═════════════════════════════════════════════════════════════
    {
        "section":        "Tech — EG",
        "color_key":      "green",
        "lead":           {"name": "Tariq Asim", "role": "Eng Team Lead"},
        "direct_members": [
            {"name": "Sabeen Fatima",      "role": ""},
            {"name": "Umama Gul Siddiqui", "role": ""},
        ],
        "sub_teams": [],
    },

    # ══ TECH — LP ═════════════════════════════════════════════════════════════
    {
        "section":        "Tech — LP",
        "color_key":      "green",
        "lead":           {"name": "Hataf Bin Atif", "role": "Eng Team Lead"},
        "direct_members": [
            {"name": "Shumaila Aslam",              "role": "DL"},
            {"name": "Unsa Umar",                   "role": "DL"},
            {"name": "Zunaira Shahid",               "role": "Eng"},
            {"name": "Muhammad Raees Shujaan Azhar", "role": "Eng"},
            {"name": "Ramisha Riaz Sheikh",          "role": "Product"},
        ],
        "sub_teams": [],
    },

    # ══ TECH — CRO ════════════════════════════════════════════════════════════
    {
        "section":        "Tech — CRO",
        "color_key":      "green",
        "lead":           {"name": "Salman Ahmad", "role": "Eng Team Lead"},
        "direct_members": [
            {"name": "Amina Tayyub",  "role": "Product"},
            {"name": "Alishba Anam",  "role": "DL"},
            {"name": "Fatima Rahman", "role": "Eng"},
        ],
        "sub_teams": [
            {
                "name":    "DL Sub-Team",
                "lead":    {"name": "Saima Bibi", "role": "DL"},
                "members": [
                    {"name": "QURAT UL AIN", "role": "DL"},
                    {"name": "Rida Nayyab",  "role": "DL"},
                ],
                "sub_teams": [],
            },
            {
                "name":    "Eng Sub-Team",
                "lead":    {"name": "Mahnoor Shafique", "role": "Eng"},
                "members": [
                    {"name": "Hassan Shahzad",  "role": "Eng"},
                    {"name": "Jahanzeb Ahmad",  "role": "Eng"},
                    {"name": "Laraib Sarfraz",  "role": "Eng"},
                ],
                "sub_teams": [],
            },
        ],
    },

    # ══ TECH — COMPLIANCE TOOL ════════════════════════════════════════════════
    {
        "section":        "Tech — Compliance Tool",
        "color_key":      "green",
        "lead":           {"name": "MUHAMMAD OMER MAZHAR RANA", "role": "Eng"},
        "direct_members": [
            {"name": "Iqra Zanib",     "role": "Eng"},
            {"name": "Saleh Muhammad", "role": "Eng"},
            {"name": "Mavia",          "role": "Product"},
        ],
        "sub_teams": [],
    },

    # ══ TECH — TRAINING FRAMEWORK ═════════════════════════════════════════════
    {
        "section":        "Tech — Training Framework",
        "color_key":      "green",
        "lead":           {"name": "Muhammad Kamran Taj", "role": "Eng Team Lead"},
        "direct_members": [
            {"name": "Muhammad Umar Raza",     "role": "Eng"},
            {"name": "Rifat Yasmeen",          "role": "DL"},
            {"name": "Afifa Sultana",          "role": "Product"},
            {"name": "Muhammad Hammad Sarfraz","role": "Eng"},
            {"name": "Muhammad Jalal Khan",    "role": "Eng"},
            {"name": "Fatima Khan",            "role": "AI-Eng"},
        ],
        "sub_teams": [],
    },

    # ══ HR ════════════════════════════════════════════════════════════════════
    {
        "section":        "HR",
        "color_key":      "purple",
        "lead":           {"name": "Zeshan Ali", "role": "Head of HR"},
        "direct_members": [
            {"name": "Aymen Abid",         "role": ""},
            {"name": "Javariya Mufarrakh", "role": ""},
            {"name": "Jawwad Ali",         "role": ""},
        ],
        "sub_teams": [
            {
                "name":    "HR Operations",
                "lead":    {"name": "Ahsan Javed", "role": "HR Operations"},
                "members": [
                    {"name": "Ayat Butt", "role": ""},
                ],
                "sub_teams": [
                    {
                        "name":    "HR Ops — Field",
                        "lead":    {"name": "Ayesha Raza Khan", "role": ""},
                        "members": [
                            {"name": "Taloot Ahmad Malik", "role": ""},
                            {"name": "Safdar Ullah",        "role": ""},
                        ],
                        "sub_teams": [],
                    },
                ],
            },
        ],
    },

    # ══ FINANCE & ACCOUNTS ════════════════════════════════════════════════════
    {
        "section":        "Finance & Accounts",
        "color_key":      "blue",
        "lead":           {"name": "Saad Zahid", "role": "Financial Controller"},
        "direct_members": [
            {"name": "Abdur Rehman Siddiqi", "role": "Data Lead"},
        ],
        "sub_teams": [
            {
                "name":    "Product / Data Team",
                "lead":    {"name": "Muhammad Zeeshan Usaid", "role": "Product"},
                "members": [
                    {"name": "Momina Raja",   "role": ""},
                    {"name": "Haroon Ali",    "role": ""},
                    {"name": "Osama Ahmad",   "role": ""},
                    {"name": "Sameer Sheikh", "role": "Data"},
                ],
                "sub_teams": [],
            },
            {
                "name":    "Dept Management",
                "lead":    {"name": "Hamza Shahid", "role": "Dpt Manager"},
                "members": [
                    {"name": "Samra Tariq",             "role": ""},
                    {"name": "Jahanzaib Ahmad",         "role": ""},
                    {"name": "Muhammad Zain ul Abadin", "role": ""},
                ],
                "sub_teams": [],
            },
        ],
    },

    # ══ IMPACT, POLICY & FUNDRAISING ══════════════════════════════════════════
    {
        "section":        "Impact, Policy & Fundraising",
        "color_key":      "blue",
        "lead":           {"name": "Sabeena Abbasi", "role": "VP / Operations"},
        "direct_members": [
            {"name": "Muhammad Usman Javed",    "role": "Fundraising"},
            {"name": "Muhammad Muzzammil Patel", "role": "Policy"},
            {"name": "Ahwaz Akhtar",             "role": "Impact"},
        ],
        "sub_teams": [],
    },

    # ══ CSO TEAM ══════════════════════════════════════════════════════════════
    {
        "section":        "CSO Team",
        "color_key":      "blue",
        "lead":           {"name": "Fahad Rao", "role": "CSO"},
        "direct_members": [],
        "sub_teams": [
            {
                "name":    "Sales — Team A",
                "lead":    {"name": "Ramsha Khurshid", "role": ""},
                "members": [
                    {"name": "Abdul Rehman Siddiqi", "role": ""},
                    {"name": "Aroma Tahir",           "role": ""},
                ],
                "sub_teams": [],
            },
            {
                "name":    "Sales — Team B",
                "lead":    {"name": "Usman Imtiaz", "role": ""},
                "members": [
                    {"name": "Muhammad Talha", "role": ""},
                ],
                "sub_teams": [],
            },
        ],
    },
]


# ── Colour palette ────────────────────────────────────────────────────────────
DARK = {
    "black":  {"red": 0.10, "green": 0.10, "blue": 0.10},
    "green":  {"red": 0.10, "green": 0.45, "blue": 0.15},
    "salmon": {"red": 0.62, "green": 0.35, "blue": 0.30},
    "blue":   {"red": 0.13, "green": 0.35, "blue": 0.62},
    "purple": {"red": 0.40, "green": 0.18, "blue": 0.50},
    "grey":   {"red": 0.35, "green": 0.35, "blue": 0.35},
}
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
LIGHT_GREY = {"red": 0.94, "green": 0.94, "blue": 0.94}


def _lighten(c, amount):
    return {k: min(v + amount, 1.0) for k, v in c.items()}


# ── Sheet column indices (0-based) ────────────────────────────────────────────
# A=0  Section
# B=1  Team Lead
# C=2  Sub-Team label
# D=3  Sub-Lead
# E=4  Member Name
# F=5  Role
NCOLS = 6


# ── Row builders ──────────────────────────────────────────────────────────────

def _blank():
    return [""] * NCOLS


def _section_row(name):
    r = _blank(); r[0] = name; return r


def _lead_row(lead):
    r = _blank(); r[1] = lead["name"]; r[5] = lead["role"]; return r


def _direct_member_row(m):
    r = _blank(); r[4] = m["name"]; r[5] = m["role"]; return r


def _subteam_label_row(name):
    r = _blank(); r[2] = name; return r


def _sublead_row(lead):
    r = _blank(); r[3] = lead["name"]; r[5] = lead["role"]; return r


def _submember_row(m):
    r = _blank(); r[4] = m["name"]; r[5] = m["role"]; return r


# ── Format request builders ───────────────────────────────────────────────────

def _fmt(sheet_id, row_start, row_end, bg, bold=False, fg=None, size=10):
    tf = {"bold": bold, "fontSize": size}
    if fg:
        tf["foregroundColor"] = fg
    return {
        "repeatCell": {
            "range": {"sheetId": sheet_id,
                      "startRowIndex": row_start, "endRowIndex": row_end},
            "cell": {"userEnteredFormat": {
                "backgroundColor": bg,
                "textFormat": tf,
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat)",
        }
    }


# ── Main sheet builder ────────────────────────────────────────────────────────

def build_rows_and_fmts(sheet_id):
    rows = [["Section", "Team Lead", "Sub-Team", "Sub-Lead", "Member Name", "Role"]]
    fmts = [_fmt(sheet_id, 0, 1,
                 {"red": 0.1, "green": 0.1, "blue": 0.1},
                 bold=True, fg=WHITE, size=11)]
    ri = 1  # current row index (0-based)

    def add(row, fmt_req=None):
        nonlocal ri
        rows.append(row)
        if fmt_req:
            fmts.append(fmt_req)
        ri += 1

    for team in ORG:
        dark = DARK[team["color_key"]]
        mid  = _lighten(dark, 0.30)
        pale = _lighten(dark, 0.52)

        # ── Section header ─────────────────────────────────────────────────
        add(_section_row(team["section"]),
            _fmt(sheet_id, ri, ri+1, dark, bold=True, fg=WHITE, size=11))

        # ── Team lead row ──────────────────────────────────────────────────
        add(_lead_row(team["lead"]),
            _fmt(sheet_id, ri, ri+1, mid, bold=True, size=10))

        # ── Direct members ─────────────────────────────────────────────────
        for m in team["direct_members"]:
            add(_direct_member_row(m),
                _fmt(sheet_id, ri, ri+1, pale))

        # ── Sub-teams (recursive, max 2 levels) ────────────────────────────
        for st in team["sub_teams"]:
            st_dark = _lighten(dark, 0.15)
            st_pale = _lighten(dark, 0.42)

            add(_subteam_label_row(st["name"]),
                _fmt(sheet_id, ri, ri+1, st_dark, bold=True, fg=WHITE, size=10))

            add(_sublead_row(st["lead"]),
                _fmt(sheet_id, ri, ri+1, _lighten(st_dark, 0.22), bold=True))

            for m in st["members"]:
                add(_submember_row(m),
                    _fmt(sheet_id, ri, ri+1, st_pale))

            # Nested sub-teams (one more level)
            for nst in st.get("sub_teams", []):
                nst_dark = _lighten(dark, 0.28)
                nst_pale = _lighten(dark, 0.55)

                add(_subteam_label_row(f"  > {nst['name']}"),
                    _fmt(sheet_id, ri, ri+1, nst_dark, bold=True, size=9))

                add(_sublead_row(nst["lead"]),
                    _fmt(sheet_id, ri, ri+1, _lighten(nst_dark, 0.18), bold=True))

                for m in nst["members"]:
                    add(_submember_row(m),
                        _fmt(sheet_id, ri, ri+1, nst_pale))

        # ── Blank separator ────────────────────────────────────────────────
        add(_blank())

    return rows, fmts


def create_sheet(services) -> dict:
    sheets = services["sheets"]
    drive  = services["drive"]

    title = f"Org Chart — Full Hierarchy ({datetime.today().strftime('%Y-%m-%d')})"

    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "Org Chart"}}],
    }).execute()

    spreadsheet_id = spreadsheet["spreadsheetId"]
    sheet_id       = spreadsheet["sheets"][0]["properties"]["sheetId"]

    rows, fmts = build_rows_and_fmts(sheet_id)

    # Write data
    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Org Chart!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    # Auto-resize + freeze header
    fmts += [
        {
            "autoResizeDimensions": {
                "dimensions": {"sheetId": sheet_id, "dimension": "COLUMNS",
                               "startIndex": 0, "endIndex": NCOLS}
            }
        },
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id,
                               "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        },
    ]

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": fmts}
    ).execute()

    file_meta = drive.files().get(
        fileId=spreadsheet_id, fields="id,name,webViewLink"
    ).execute()

    return {"id": spreadsheet_id, "title": file_meta["name"], "url": file_meta["webViewLink"],
            "rows": len(rows)}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Org Chart with Sub-Divisions (Canva organogram, April 2026)")
    total_members = 0
    for t in ORG:
        dm = len(t["direct_members"])
        sm = sum(len(s["members"]) + sum(len(n["members"]) for n in s.get("sub_teams", []))
                 for s in t["sub_teams"])
        total = dm + sm
        total_members += total
        subs = f" | sub-teams: {[s['name'] for s in t['sub_teams']]}" if t["sub_teams"] else ""
        print(f"  [{t['section']}]  Lead: {t['lead']['name']}  | direct: {dm}  | sub-member: {sm}{subs}")

    print(f"\n  {len(ORG)} sections | ~{total_members} members total")

    confirm = input("\nCreate Google Sheet? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    print("\nConnecting to Google services...")
    services = get_google_services()
    print("Building sheet...")
    result = create_sheet(services)

    print(f"\nDone!")
    print(f"  Title : {result['title']}")
    print(f"  Rows  : {result['rows']}")
    print(f"  Link  : {result['url']}")


if __name__ == "__main__":
    main()
