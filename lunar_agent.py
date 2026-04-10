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
        "department":   "—",
        "entity":       "—",
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

    # ── scan Gmail for new joiners ─────────────────────────────────────────────
    print("\nScanning Gmail for new joiners…")
    new_joiners = scan_gmail_for_new_joiners(gmail, existing_names)

    if new_joiners:
        print(f"  → {len(new_joiners)} new joiner(s) detected:")
        for emp in new_joiners:
            print(f"    + {emp['name']}  (joined {emp['joining_date']}  |  {emp['designation']})")
    else:
        print("  → No new joiners found in Gmail.")

    # ── append new joiner rows ────────────────────────────────────────────────
    if new_joiners:
        # Find the last data row to append after
        last_data_row = data_rows[-1][0] if data_rows else 3
        next_sr = int(rows[data_rows[-1][0] - 1][COL_SR]) + 1 if data_rows else 1

        for emp in new_joiners:
            next_row  = last_data_row + 1
            prob_end  = emp["joining_date"] + relativedelta(months=PROBATION_MONTHS)
            days_str, status = calc_status(emp["joining_date"], today)

            row_values = [
                next_sr,
                emp["name"],
                emp["designation"],
                emp["department"],
                emp["entity"],
                emp["joining_date"].strftime("%d %b %Y"),
                prob_end.strftime("%d %b %Y"),
                days_str,
                status,
                "Contract email detected via Gmail",
                today_str,
                "Pending closure email",
            ]

            if not dry_run:
                # Append as a new row
                sheets.spreadsheets().values().append(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"'{tab}'!A{next_row}",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [row_values]},
                ).execute()
                print(f"  ✓ Added {emp['name']} to sheet (row {next_row})")
            else:
                print(f"  [DRY RUN] Would add {emp['name']} to sheet (row {next_row})")

            last_data_row += 1
            next_sr += 1
            summary_lines.append(f"  NEW: {emp['name']} joined {emp['joining_date']} — added to sheet")

    # ── write updates to sheet ────────────────────────────────────────────────
    if updates:
        if not dry_run:
            print(f"\nWriting {len(updates)} cell updates to sheet…", end=" ", flush=True)
            try:
                write_cells(sheets, SPREADSHEET_ID, tab, updates)
                print("Done.")
            except Exception as e:
                print(f"FAILED\n✗ {e}")
                sys.exit(1)
        else:
            print(f"\n[DRY RUN] Would write {len(updates)} cell updates.")

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
