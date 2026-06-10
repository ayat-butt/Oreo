#!/usr/bin/env python3
"""
Lunar — Daily Probation Tracker Agent
======================================
Runs at 9:30 AM PKT (04:30 UTC) every day.

Daily tasks:
  1. Recalculate Days Left/Overdue and Status for every employee in the
     probation tracker Google Sheet.
  2. Scan Gmail for new contract/offer emails and add new joiners to the sheet.

Usage:
  python lunar_agent.py            # normal daily run
  python lunar_agent.py --dry-run  # preview changes without writing to sheet
"""

import sys
import io
import re
import json
import base64
import argparse
from datetime import date, datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from dateutil.relativedelta import relativedelta
from googleapiclient.discovery import Resource

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
STATE_FILE = ROOT / "lunar_state.json"   # tracks last-run date + known employees
LOG_DIR    = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── sheet config ───────────────────────────────────────────────────────────────
SPREADSHEET_ID = "1_yvL_lM3WzE5BBzsk60PO7gutsYer_y1PSFbTT0hJBY"
SHEET_GID      = 322356645   # numeric gid of the probation tracker tab

# Column indices — 0-based (A=0, B=1 …)
COL_SR       = 0   # A  #
COL_NAME     = 1   # B  Name
COL_DESIG    = 2   # C  Designation
COL_DEPT     = 3   # D  Department
COL_ENTITY   = 4   # E  Entity
COL_JOINED   = 5   # F  Date of Joining   e.g. "01 Oct 2025"
COL_PROB_END = 6   # G  Probation End Date
COL_DAYS     = 7   # H  Days Overdue / Left
COL_STATUS   = 8   # I  Status
COL_CONTRACT = 9   # J  Contract on Record
COL_DATE     = 10  # K  Contract Date
COL_CLOSURE  = 11  # L  Probation Closure Status

PROBATION_MONTHS = 3

# Gmail search queries for new joiner detection.
# Day 01 email is the most reliable: Ayat sends it for every new hire and
# the body always contains "starting ... from [date]" or "joining date is [date]".
# newer_than:120d limits to emails from the last 4 months to avoid picking up old employees.
GMAIL_CONTRACT_QUERIES = [
    'from:me subject:"What to Expect on Your Day 01" newer_than:120d',
    'from:me subject:"Welcome to Taleemabad" newer_than:120d',
]

# Joining dates older than this many days are assumed to be already tracked
MAX_JOINER_LOOKBACK_DAYS = 120

# ── exclusions ──────────────────────────────────────────────────────────────────
# Employees who must NEVER be auto-added to the probation tracker.
# The Audio Monitoring Officer (Assessments) team is tracked separately by HR and
# was deliberately kept out of the tracker (instruction from Ayat, 2026-06-10).
EXCLUDED_EMAILS = {
    "kaynatsyeda4@gmail.com",     # Syeda Kaynat Bukhari   (Audio Monitoring)
    "laraibsyed1999@gmail.com",   # Laraib Syed            (Audio Monitoring)
    "gulrukhdinal@gmail.com",     # Gulrukh Dinal          (Audio Monitoring)
    "arshadkhan285981@gmail.com", # Arshad Khan            (Audio Monitoring)
    "shaikhfareeda8@gmail.com",   # Fareeda Shaikh         (Audio Monitoring)
    "zamanmuddasir44@gmail.com",  # Muddasir Zaman         (Audio Monitoring)
    "muhammadfgs7@gmail.com",     # Muhammad Ahmed — offer fell through, not joining (2026-06-10)
    "raiyaanjhamid@gmail.com",    # Raiyaan Hamid  — offer fell through, not joining (2026-06-10)
}
# Names that must never be auto-added (offers that fell through, deliberate
# removals). Matched case-insensitively against the extracted full name.
EXCLUDED_NAMES = {
    "muhammad ahmed",
    "raiyaan hamid",
    "mohammed raiyaan junaid hamid",
}
# Any new-joiner email whose subject contains one of these phrases is skipped —
# catches future Audio Monitoring hires even if their address isn't listed above.
EXCLUDED_SUBJECT_KEYWORDS = ["audio monitoring"]

# ── date helpers ───────────────────────────────────────────────────────────────
DATE_FORMATS = [
    "%d %b %Y",   # 01 Oct 2025
    "%d-%b-%Y",   # 01-Oct-2025
    "%Y-%m-%d",   # 2025-10-01
    "%d/%m/%Y",   # 01/10/2025
    "%B %d, %Y",  # October 1, 2025
    "%d %B %Y",   # 01 October 2025
]


def parse_date(s: str) -> date | None:
    """Try multiple date formats. Return None if unparseable."""
    s = s.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def calc_status(joined: date, today: date) -> tuple[str, str]:
    """Return (days_str, status_label) based on joining date and today."""
    prob_end  = joined + relativedelta(months=PROBATION_MONTHS)
    days_left = (prob_end - today).days

    if days_left < 0:
        overdue = abs(days_left)
        days_str = f"-{overdue} days"
        status   = f"Completed — {overdue}d overdue"
    elif days_left == 0:
        days_str = "0 days"
        status   = "Probation Ends TODAY"
    elif days_left <= 30:
        days_str = f"{days_left} days"
        status   = "In 3rd Month — Ending Soon"
    elif days_left <= 60:
        days_str = f"{days_left} days"
        status   = "In 2nd Month — Upcoming"
    else:
        days_str = f"{days_left} days"
        status   = "In 1st Month"

    return days_str, status


# ── sheet helpers ──────────────────────────────────────────────────────────────

def find_tab_name(sheets: Resource, spreadsheet_id: str, gid: int) -> str:
    """Resolve a numeric gid to its sheet tab name."""
    meta = sheets.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        if props.get("sheetId") == gid:
            return props["title"]
    raise ValueError(f"No sheet with gid={gid} found in spreadsheet {spreadsheet_id}")


def read_all_rows(sheets: Resource, spreadsheet_id: str, tab: str) -> list[list]:
    """Read all rows from the sheet tab. Returns list of row-lists."""
    result = sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{tab}'",
    ).execute()
    return result.get("values", [])


def write_cells(sheets: Resource, spreadsheet_id: str, tab: str,
                updates: list[dict]) -> None:
    """
    Batch-write cell updates.
    updates = [{"range": "A5", "value": "text"}, …]
    """
    data = [
        {
            "range": f"'{tab}'!{u['range']}",
            "values": [[u["value"]]],
        }
        for u in updates
    ]
    body = {"valueInputOption": "USER_ENTERED", "data": data}
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body
    ).execute()


def col_letter(idx: int) -> str:
    """0-based column index → letter(s). 0→A, 25→Z, 26→AA …"""
    result = ""
    idx += 1
    while idx:
        idx, rem = divmod(idx - 1, 26)
        result = chr(65 + rem) + result
    return result


# ── template-aware new-joiner insertion ─────────────────────────────────────────
# The tracker groups employees under "<Month YYYY> Joiners" section headers and uses
# 13 columns (A–M, M = "Requirement"). New joiners must be inserted under the correct
# month section — not appended at the bottom — so the sheet's template stays intact.

SECTION_SUFFIX = " Joiners"


def _section_key(label: str) -> date | None:
    """'October 2025 Joiners' → date(2025,10,1). None if not a month section."""
    try:
        return datetime.strptime(label.replace(SECTION_SUFFIX, "").strip(), "%B %Y").date()
    except ValueError:
        return None


def build_sheet_model(rows: list[list]) -> tuple[int | None, list[dict], list[int]]:
    """
    Parse the sheet into (header_idx, sections, data_idx), all 0-based.
      header_idx : index of the '#'/'Name' header row
      sections   : [{'label','idx','key'}] for each '<Month YYYY> Joiners' header
      data_idx   : indices of data rows (col A is an integer)
    """
    header_idx = None
    for i, r in enumerate(rows):
        if r and str(r[0]).strip() == "#":
            header_idx = i
            break

    sections: list[dict] = []
    data_idx: list[int] = []
    for i, r in enumerate(rows):
        if not r:
            continue
        a = str(r[0]).strip()
        if a.isdigit():
            data_idx.append(i)
        elif header_idx is not None and i > header_idx and a:
            key = _section_key(a)
            if key:
                sections.append({"label": a, "idx": i, "key": key})
    return header_idx, sections, data_idx


def _build_joiner_row(emp: dict, today: date) -> list:
    """Build a 13-column row (A–M) matching the sheet template. Serial (A) left
    blank — filled by the renumber pass. Human-curated fields (Department, Entity,
    Contract Date, Requirement) left blank for HR rather than fabricated."""
    jd       = emp["joining_date"]
    prob_end = jd + relativedelta(months=PROBATION_MONTHS)
    days_str, status = calc_status(jd, today)
    return [
        "",                                              # A  # (renumber pass fills)
        emp["name"],                                     # B  Name
        emp.get("designation") or "—",                   # C  Designation
        emp.get("department") or "",                     # D  Department  (HR fills)
        emp.get("entity") or "",                          # E  Entity      (HR fills)
        jd.strftime("%d %b %Y"),                          # F  Date of Joining
        prob_end.strftime("%d %b %Y"),                    # G  Probation End
        days_str,                                         # H  Days
        status,                                           # I  Status
        emp.get("subject") or "Welcome email on record",  # J  Contract on Record
        "",                                               # K  Contract Date (HR fills)
        f"Not sent — due {prob_end.strftime('%d %b %Y')}",# L  Closure status
        "",                                               # M  Requirement  (HR fills)
    ]


def _insert_blank_rows(sheets: Resource, spreadsheet_id: str, sheet_gid: int,
                       start_idx: int, count: int) -> None:
    """Insert `count` blank rows at 0-based `start_idx`, inheriting formatting."""
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"insertDimension": {
            "range": {"sheetId": sheet_gid, "dimension": "ROWS",
                      "startIndex": start_idx, "endIndex": start_idx + count},
            "inheritFromBefore": start_idx > 0,
        }}]},
    ).execute()


def _write_row(sheets: Resource, spreadsheet_id: str, tab: str,
               row_1based: int, values: list) -> None:
    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"'{tab}'!A{row_1based}",
        valueInputOption="USER_ENTERED",
        body={"values": [values]},
    ).execute()


def plan_joiner_insert(rows: list[list], emp: dict, today: date) -> dict | None:
    """
    Work out where a joiner's row (and possibly a new section header) should go.
    Returns a plan dict, or None if the sheet structure can't be parsed (guard).
      {'label', 'new_section', 'section_at' (0-based or None),
       'data_at' (0-based), 'values'}
    """
    header_idx, sections, data_idx = build_sheet_model(rows)
    if header_idx is None:
        return None  # unrecognised structure — refuse to write

    jd    = emp["joining_date"]
    label = f"{jd.strftime('%B %Y')}{SECTION_SUFFIX}"
    key   = jd.replace(day=1)
    values = _build_joiner_row(emp, today)

    target = next((s for s in sections if s["key"] == key), None)
    if target:
        nxt = min([s["idx"] for s in sections if s["idx"] > target["idx"]],
                  default=len(rows))
        sec_data = [d for d in data_idx if target["idx"] < d < nxt]
        data_at = (max(sec_data) if sec_data else target["idx"]) + 1
        return {"label": label, "new_section": False, "section_at": None,
                "data_at": data_at, "values": values}

    # section missing — create it in chronological order
    later = sorted([s for s in sections if s["key"] > key], key=lambda s: s["key"])
    if later:
        section_at = later[0]["idx"]
    else:
        section_at = (max(data_idx) + 1) if data_idx else (header_idx + 1)
    return {"label": label, "new_section": True, "section_at": section_at,
            "data_at": section_at + 1, "values": values}


def renumber_serials(sheets: Resource, spreadsheet_id: str, tab: str,
                     dry_run: bool) -> list[dict]:
    """Rewrite column A so data rows are numbered 1..N in sheet order."""
    rows = read_all_rows(sheets, spreadsheet_id, tab)
    updates, n = [], 0
    for i, r in enumerate(rows):
        if r and str(r[0]).strip().isdigit():
            n += 1
            if str(r[0]).strip() != str(n):
                updates.append({"range": f"A{i + 1}", "value": n})
    if updates and not dry_run:
        write_cells(sheets, spreadsheet_id, tab, updates)
    return updates


def insert_joiners_matching_template(sheets: Resource, spreadsheet_id: str, tab: str,
                                     sheet_gid: int, new_joiners: list[dict],
                                     today: date, dry_run: bool) -> list[str]:
    """Insert each new joiner under the correct month section, creating the section
    header if needed, then renumber serials. Returns human-readable summary lines."""
    summary: list[str] = []
    for emp in sorted(new_joiners, key=lambda e: e["joining_date"]):
        rows = read_all_rows(sheets, spreadsheet_id, tab)  # re-read: indices shift per insert
        plan = plan_joiner_insert(rows, emp, today)
        if plan is None:
            msg = f"  ⚠ SKIPPED {emp['name']} — could not parse sheet template, refusing to write"
            print(msg)
            summary.append(msg)
            continue

        sec_note = f"new section '{plan['label']}' + " if plan["new_section"] else ""
        if dry_run:
            print(f"  [DRY RUN] {emp['name']} → {sec_note}row {plan['data_at'] + 1} "
                  f"under '{plan['label']}'")
            summary.append(f"  NEW: {emp['name']} joined {emp['joining_date']} "
                           f"→ would add under '{plan['label']}'")
            continue

        if plan["new_section"]:
            _insert_blank_rows(sheets, spreadsheet_id, sheet_gid, plan["section_at"], 2)
            _write_row(sheets, spreadsheet_id, tab, plan["section_at"] + 1, [plan["label"]])
            _write_row(sheets, spreadsheet_id, tab, plan["data_at"] + 1, plan["values"])
        else:
            _insert_blank_rows(sheets, spreadsheet_id, sheet_gid, plan["data_at"], 1)
            _write_row(sheets, spreadsheet_id, tab, plan["data_at"] + 1, plan["values"])

        print(f"  ✓ Added {emp['name']} under '{plan['label']}' "
              f"(needs HR: Department, Entity, Contract Date, Requirement)")
        summary.append(f"  NEW: {emp['name']} joined {emp['joining_date']} "
                       f"→ added under '{plan['label']}' (Dept/Entity/Contract Date/Requirement blank)")

    renum = renumber_serials(sheets, spreadsheet_id, tab, dry_run)
    if renum:
        print(f"  {'[DRY RUN] would renumber' if dry_run else '✓ renumbered'} "
              f"{len(renum)} serial number(s)")
    return summary


# ── Gmail helpers ──────────────────────────────────────────────────────────────

def _decode_body(msg: dict) -> str:
    """Extract text body from a Gmail message (plain text preferred, HTML fallback)."""
    def _extract(part: dict) -> str:
        mime = part.get("mimeType", "")
        data = part.get("body", {}).get("data", "")
        if data and "plain" in mime:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        for sub in part.get("parts", []):
            result = _extract(sub)
            if result:
                return result
        # HTML fallback — strip tags
        if data and "html" in mime:
            raw = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            raw = re.sub(r"<[^>]+>", " ", raw)
            return re.sub(r"\s+", " ", raw)
        return ""
    return _extract(msg.get("payload", {}))


def _extract_name_from_subject(subject: str) -> str | None:
    """
    Try to extract an employee name from common subject patterns:
      'Offer Letter CPD Coach | Saaim Asif'  → 'Saaim Asif'
      'Welcome to Taleemabad - Full Stack Developer'  → None (no name here)
    """
    # Pattern: text | Name
    pipe_match = re.search(r"\|\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", subject)
    if pipe_match:
        return pipe_match.group(1).strip()
    # Pattern: Congratulations, Name!  or  Congratulations Name
    congrats = re.search(r"Congratulations[,\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", subject)
    if congrats:
        return congrats.group(1).strip()
    return None


def _extract_name_from_body(body: str) -> str | None:
    """Extract employee first name from Day 01 email greeting: 'Hi Zeest,' or 'Dear Muhammad Usman,'."""
    m = re.search(r"(?:Hi|Dear)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s*[,\n]", body)
    if m:
        name = m.group(1).strip()
        # Exclude generic openers
        if name.lower() not in ("team", "all", "everyone", "colleagues", "sir", "ma"):
            return name
    return None


def _extract_joining_date_from_body(body: str) -> date | None:
    """Scan email body for joining date phrases used in Ayat's onboarding emails."""
    patterns = [
        # "starting remotely from 7th April 2026"  /  "starting from 7 April 2026"
        r"starting\s+(?:remotely\s+)?from\s+(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})",
        # "official joining date is Monday, 16th February"  (year may be absent)
        r"joining\s+date\s+is\s+(?:[A-Za-z]+,\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+(?:\s+\d{4})?)",
        # "joining date: 01 Apr 2026"
        r"(?:Date of Joining|Joining Date|Start Date)[:\s]+([0-9]{1,2}[\s\-/][A-Za-z]+[\s\-/][0-9]{4})",
        # "joining arrangement, you will be starting ... 7th April 2026"
        r"(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]{3,9}\s+\d{4})",  # broad fallback
    ]
    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            raw = re.sub(r"(?:st|nd|rd|th)", "", match.group(1))  # strip ordinals
            d = parse_date(raw.strip())
            if d and d.year >= 2025:   # sanity check — only recent dates
                return d
    return None


def _extract_employee_details(subject: str, body: str, to_header: str) -> dict | None:
    """
    Extract {name, joining_date, designation} from a new-joiner email.
    Priority for name: To header (most reliable full name) > subject pipe > body greeting.
    Returns None if joining date cannot be determined.
    """
    # Name: To header first (e.g. "Zeest Qureshi <zeest@gmail.com>" → "Zeest Qureshi")
    name = None
    if to_header:
        # Handle multiple recipients — take the first one
        first_recipient = to_header.split(",")[0].strip()
        m = re.match(r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)\s*<", first_recipient)
        if m:
            name = m.group(1).strip()
    if not name:
        name = _extract_name_from_subject(subject)
    if not name:
        name = _extract_name_from_body(body)

    joining_date = _extract_joining_date_from_body(body)

    # Designation: extract from subject
    desig = "—"
    subject_lower = subject.lower()
    # "Welcome to Taleemabad - Senior Manager Growth" → "Senior Manager Growth"
    dash_match = re.search(
        r"(?:welcome to taleemabad|offer letter)[^-]*-\s*(?:at taleemabad\s*[|]\s*)?(.+?)(?:\s*[|]|$)",
        subject, re.IGNORECASE
    )
    if dash_match:
        desig = dash_match.group(1).strip()
    else:
        # Fall back to keyword scan
        for kw in ["Full Stack Developer", "Sr. Manager", "Senior Manager", "Manager",
                   "Coach", "Fellow", "Coordinator", "COO", "CFO", "Executive",
                   "Officer", "Associate", "Analyst", "Engineer", "Director"]:
            if kw.lower() in subject_lower:
                desig = kw
                break

    if not name or not joining_date:
        return None

    return {
        "name":         name,
        "joining_date": joining_date,
        "designation":  desig,
        "department":   "",      # not derivable from email — HR fills
        "entity":       "",      # not derivable from email — HR fills
        "subject":      subject.strip(),
    }


def scan_gmail_for_new_joiners(
    gmail: Resource,
    existing_names: set[str],
) -> list[dict]:
    """
    Search Gmail for new-joiner emails. Return list of employees
    not already tracked in the sheet.
    """
    # Never add the HR manager herself as a new employee
    HR_MANAGER_FIRST_NAMES = {"ayat", "ayat butt"}
    found: dict[str, dict] = {}   # name → details

    for query in GMAIL_CONTRACT_QUERIES:
        # queries already include from:me — don't double-prepend
        try:
            results = gmail.users().messages().list(
                userId="me", q=query, maxResults=50
            ).execute()
        except Exception as e:
            print(f"  [Gmail] Query failed ({query[:50]}): {e}")
            continue

        messages = results.get("messages", [])
        for msg_ref in messages:
            try:
                msg = gmail.users().messages().get(
                    userId="me",
                    id=msg_ref["id"],
                    format="full",
                ).execute()
            except Exception:
                continue

            headers = {h["name"]: h["value"]
                       for h in msg.get("payload", {}).get("headers", [])}
            subject   = headers.get("Subject", "")
            to_header = headers.get("To", "")

            # Skip explicitly-excluded teams (e.g. Audio Monitoring — tracked
            # separately by HR and intentionally kept out of the tracker).
            if any(kw in subject.lower() for kw in EXCLUDED_SUBJECT_KEYWORDS):
                continue
            if any(addr in to_header.lower() for addr in EXCLUDED_EMAILS):
                continue

            body      = _decode_body(msg)

            details = _extract_employee_details(subject, body, to_header)
            if not details:
                continue

            # Sanity check: joining date must be recent (within lookback window)
            days_since_joining = (date.today() - details["joining_date"]).days
            if days_since_joining > MAX_JOINER_LOOKBACK_DAYS:
                continue

            name = details["name"].strip()
            name_lower = name.lower()

            # Skip people who must never be auto-added (offers fell through, etc.)
            if name_lower in EXCLUDED_NAMES:
                continue

            is_hr_manager = (
                name_lower in HR_MANAGER_FIRST_NAMES
                or name_lower.split()[0] in HR_MANAGER_FIRST_NAMES
            )
            if is_hr_manager:
                continue

            # Word-overlap deduplication: if any significant word (>2 chars) from
            # the found name appears in any existing sheet name, skip as duplicate.
            sig_words = {w for w in re.sub(r"[^a-z\s]", "", name_lower).split() if len(w) > 2}
            already_tracked = any(
                sig_words & {w for w in re.sub(r"[^a-z\s]", "", ex).split() if len(w) > 2}
                for ex in existing_names
            )
            # Require at least two words — single first-names are too ambiguous to auto-add
            if len(name.split()) < 2:
                continue

            if not already_tracked and name not in found:
                found[name] = details

    return list(found.values())


# ── state management ───────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_run": None, "known_employees": []}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


# ── main logic ─────────────────────────────────────────────────────────────────

def run(dry_run: bool = False) -> None:
    today     = date.today()
    today_str = today.strftime("%Y-%m-%d")

    print(f"\n{'='*60}")
    print(f"  Lunar — Probation Tracker Update")
    print(f"  Date: {today_str}  |  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*60}\n")

    # ── connect ────────────────────────────────────────────────────────────────
    print("Connecting to Google services…", end=" ", flush=True)
    try:
        import sys
        sys.path.insert(0, str(ROOT))
        from hr_assistant.config import get_google_services
        services = get_google_services()
        print("OK")
    except Exception as e:
        print(f"FAILED\n✗ {e}")
        sys.exit(1)

    sheets = services["sheets"]
    gmail  = services["gmail"]

    # ── find tab ───────────────────────────────────────────────────────────────
    print(f"Locating sheet tab (gid={SHEET_GID})…", end=" ", flush=True)
    try:
        tab = find_tab_name(sheets, SPREADSHEET_ID, SHEET_GID)
        print(f"'{tab}'")
    except Exception as e:
        print(f"FAILED\n✗ {e}")
        sys.exit(1)

    # ── read sheet ─────────────────────────────────────────────────────────────
    print("Reading probation tracker…", end=" ", flush=True)
    rows = read_all_rows(sheets, SPREADSHEET_ID, tab)
    print(f"{len(rows)} rows read")

    # ── identify data rows ────────────────────────────────────────────────────
    # Data rows have a number in col A (serial number). Rows 0-2 are title/note/headers.
    data_rows: list[tuple[int, list]] = []   # (1-based row number, row_data)
    existing_names: set[str] = set()

    for i, row in enumerate(rows):
        if not row:
            continue
        try:
            int(str(row[COL_SR]).strip())
            data_rows.append((i + 1, row))  # i+1 = 1-based sheet row
            if len(row) > COL_NAME:
                # Store lowercased for case-insensitive matching
                existing_names.add(row[COL_NAME].strip().lower())
        except (ValueError, IndexError):
            continue

    print(f"  → {len(data_rows)} employee rows found")

    # ── recalculate existing rows ──────────────────────────────────────────────
    print("\nRecalculating probation status…")
    updates: list[dict] = []
    summary_lines: list[str] = []

    for sheet_row, row in data_rows:
        if len(row) <= COL_JOINED:
            continue
        raw_date = row[COL_JOINED].strip()
        joined   = parse_date(raw_date)
        if not joined:
            print(f"  ⚠ Could not parse date '{raw_date}' for {row[COL_NAME] if len(row) > COL_NAME else '?'} — skipping")
            continue

        name                   = row[COL_NAME].strip() if len(row) > COL_NAME else "?"
        prob_end               = joined + relativedelta(months=PROBATION_MONTHS)
        new_days_str, new_status = calc_status(joined, today)

        old_days   = row[COL_DAYS].strip()   if len(row) > COL_DAYS   else ""
        old_status = row[COL_STATUS].strip() if len(row) > COL_STATUS else ""

        changed = (old_days != new_days_str) or (old_status != new_status)

        updates.append({"range": f"{col_letter(COL_PROB_END)}{sheet_row}", "value": prob_end.strftime("%d %b %Y")})
        updates.append({"range": f"{col_letter(COL_DAYS)}{sheet_row}",     "value": new_days_str})
        updates.append({"range": f"{col_letter(COL_STATUS)}{sheet_row}",   "value": new_status})

        flag = "✦ CHANGED" if changed else "  ok"
        print(f"  {flag}  {name:<30} {new_days_str:>12}  |  {new_status}")
        if changed:
            summary_lines.append(f"  {name}: {old_days} → {new_days_str}  |  {old_status} → {new_status}")

    # ── write recalculated status to sheet FIRST ───────────────────────────────
    # Must happen before inserting new-joiner rows: inserts shift row positions,
    # and these updates are keyed by absolute row number.
    if updates:
        if not dry_run:
            print(f"\nWriting {len(updates)} status updates to sheet…", end=" ", flush=True)
            try:
                write_cells(sheets, SPREADSHEET_ID, tab, updates)
                print("Done.")
            except Exception as e:
                print(f"FAILED\n✗ {e}")
                sys.exit(1)
        else:
            print(f"\n[DRY RUN] Would write {len(updates)} status updates.")

    # ── scan Gmail for new joiners ─────────────────────────────────────────────
    print("\nScanning Gmail for new joiners…")
    new_joiners = scan_gmail_for_new_joiners(gmail, existing_names)

    if new_joiners:
        print(f"  → {len(new_joiners)} new joiner(s) detected:")
        for emp in new_joiners:
            print(f"    + {emp['name']}  (joined {emp['joining_date']}  |  {emp['designation']})")
        # Insert each under its month section (creating the header if missing) so
        # the sheet template stays intact, then renumber serials.
        summary_lines.extend(
            insert_joiners_matching_template(
                sheets, SPREADSHEET_ID, tab, SHEET_GID,
                new_joiners, today, dry_run,
            )
        )
    else:
        print("  → No new joiners found in Gmail.")

    # ── update title row with today's date ────────────────────────────────────
    month_label = today.strftime("%B %Y")
    new_title   = (
        f"Probation Status Report — {month_label}  |  "
        f"Active Employees Only  |  "
        f"Last updated by Lunar: {today_str}"
    )
    if not dry_run:
        write_cells(sheets, SPREADSHEET_ID, tab,
                    [{"range": "A1", "value": new_title}])

    # ── run summary ───────────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  Lunar Run Summary — {today_str}")
    print(f"{'─'*60}")
    print(f"  Employees updated : {len(data_rows)}")
    print(f"  New joiners added : {len(new_joiners)}")
    print(f"  Status changes    : {len(summary_lines)}")
    if summary_lines:
        print()
        for line in summary_lines:
            print(line)
    print(f"{'─'*60}\n")

    # ── persist state ─────────────────────────────────────────────────────────
    state = load_state()
    state["last_run"]         = today_str
    state["known_employees"]  = list(existing_names | {e["name"] for e in new_joiners})
    save_state(state)

    # ── write log ─────────────────────────────────────────────────────────────
    log_path = LOG_DIR / f"lunar_{today_str}.log"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Lunar run — {today_str}\n")
        f.write(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")
        f.write(f"Employees updated: {len(data_rows)}\n")
        f.write(f"New joiners: {len(new_joiners)}\n")
        f.write(f"Changes:\n")
        for line in summary_lines:
            f.write(f"{line}\n")
    print(f"Log saved → {log_path}")


# ── entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lunar — Daily Probation Tracker Agent")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing to the sheet")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
