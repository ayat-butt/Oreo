#!/usr/bin/env python3
"""
One-time cleanup of the probation tracker:
  1. Create "April 2026 Joiners" and "May 2026 Joiners" section headers (matching
     the existing headers' colour / bold / merge formatting).
  2. Regroup misfiled rows (Zeest, Irum, Abu Bakr → April; Rahima → May) by
     placing the new headers in the right spots.
  3. Fix the two corrupt auto-added rows (Abu Bakr, Rahima): J/K/L columns.
  4. Renumber all serials 1..N.
"""
import sys
sys.path.insert(0, ".")
import lunar_agent as L
from hr_assistant.config import get_google_services

GID = L.SHEET_GID
sheets = get_google_services()["sheets"]
SID = L.SPREADSHEET_ID
tab = L.find_tab_name(sheets, SID, GID)

MODEL_HEADER_ROW0 = 29  # 0-based index of "March 2026 Joiners" — the format model
NCOLS = 13              # A..M


def find_row_by_name(rows, name):
    """Return 1-based sheet row for a data row whose Name (col B) matches."""
    for i, r in enumerate(rows):
        if len(r) > 1 and str(r[0]).strip().isdigit() and r[1].strip() == name:
            return i + 1
    return None


def find_section_target(rows, before_name):
    """0-based index where a new header should be inserted (right before the row
    of `before_name`)."""
    for i, r in enumerate(rows):
        if len(r) > 1 and r[1].strip() == before_name:
            return i
    raise ValueError(f"{before_name} not found")


rows = L.read_all_rows(sheets, SID, tab)

# ── Step 1: insert the two header rows (bottom-up so indices stay valid) ──────────
may_at  = find_section_target(rows, "Rahima Omar")            # May header before Rahima
apr_at  = find_section_target(rows, "Zeest Hassan Qureshi")   # April header before Zeest
print(f"Inserting May header at row {may_at+1}, April header at row {apr_at+1} (1-based)")

sheets.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": [
    {"insertDimension": {"range": {"sheetId": GID, "dimension": "ROWS",
        "startIndex": may_at, "endIndex": may_at + 1}, "inheritFromBefore": True}},
    {"insertDimension": {"range": {"sheetId": GID, "dimension": "ROWS",
        "startIndex": apr_at, "endIndex": apr_at + 1}, "inheritFromBefore": True}},
]}).execute()

# After both inserts: April header lands at apr_at, May header at may_at+1
apr_hdr = apr_at
may_hdr = may_at + 1

# ── Step 2: copy header formatting + merge the two new header rows ───────────────
def fmt_and_merge(dst0):
    return [
        {"copyPaste": {
            "source":      {"sheetId": GID, "startRowIndex": MODEL_HEADER_ROW0,
                            "endRowIndex": MODEL_HEADER_ROW0 + 1,
                            "startColumnIndex": 0, "endColumnIndex": NCOLS},
            "destination": {"sheetId": GID, "startRowIndex": dst0, "endRowIndex": dst0 + 1,
                            "startColumnIndex": 0, "endColumnIndex": NCOLS},
            "pasteType": "PASTE_FORMAT"}},
        {"mergeCells": {"range": {"sheetId": GID, "startRowIndex": dst0, "endRowIndex": dst0 + 1,
            "startColumnIndex": 0, "endColumnIndex": NCOLS}, "mergeType": "MERGE_ALL"}},
    ]

sheets.spreadsheets().batchUpdate(spreadsheetId=SID, body={
    "requests": fmt_and_merge(apr_hdr) + fmt_and_merge(may_hdr)
}).execute()

# ── Step 3: write the header labels ──────────────────────────────────────────────
L.write_cells(sheets, SID, tab, [
    {"range": f"A{apr_hdr + 1}", "value": "April 2026 Joiners"},
    {"range": f"A{may_hdr + 1}", "value": "May 2026 Joiners"},
])
print(f"Wrote headers: 'April 2026 Joiners' (row {apr_hdr+1}), 'May 2026 Joiners' (row {may_hdr+1})")

# ── Step 4: fix the two corrupt rows (find by name, robust to index shifts) ──────
rows = L.read_all_rows(sheets, SID, tab)
ab = find_row_by_name(rows, "Abu Bakr")
ra = find_row_by_name(rows, "Rahima Omar")
fixes = [
    {"range": f"J{ab}", "value": "Welcome email on record"},
    {"range": f"K{ab}", "value": ""},
    {"range": f"L{ab}", "value": "Not sent — due 30 Jul 2026"},
    {"range": f"J{ra}", "value": "Welcome to Taleemabad - Junior Research Associate (Impact & Policy)"},
    {"range": f"K{ra}", "value": ""},
    {"range": f"L{ra}", "value": "Not sent — due 06 Aug 2026"},
]
L.write_cells(sheets, SID, tab, fixes)
print(f"Fixed Abu Bakr (row {ab}) and Rahima Omar (row {ra}) J/K/L columns")

# ── Step 5: renumber serials ─────────────────────────────────────────────────────
renum = L.renumber_serials(sheets, SID, tab, dry_run=False)
print(f"Renumbered {len(renum)} serial(s)")
print("Cleanup complete.")
