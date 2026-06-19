#!/usr/bin/env python3
"""Highlight all duplicate entries on the tracker sheet."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from collections import defaultdict
from hr_assistant.config import get_google_services

TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

def normalize_name(name):
    """Normalize name for matching."""
    return name.lower().strip().replace("  ", " ")

def read_tracker_sheet():
    """Read tracker sheet."""
    services = get_google_services()
    sheets = services["sheets"]

    metadata = sheets.spreadsheets().get(spreadsheetId=TRACKER_SHEET_ID).execute()
    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == TRACKER_GID:
            sheet_name = sheet["properties"]["title"]
            break

    result = sheets.spreadsheets().values().get(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'{sheet_name}'!A1:G500"
    ).execute()

    return result.get("values", []), sheet_name

def main():
    print("="*120)
    print("HIGHLIGHTING DUPLICATE ENTRIES ON SHEET")
    print("="*120)

    print("\n[1] Reading tracker sheet...")
    tracker_rows, sheet_name = read_tracker_sheet()
    print(f"    ✓ {len(tracker_rows)} rows read")

    # Track all names and their positions
    name_positions = defaultdict(list)  # {normalized_name: [(row, col, actual_name)]}

    print("\n[2] Scanning for duplicates...")
    for row_idx, row in enumerate(tracker_rows[1:], start=2):  # Skip header
        # Column B: SMT
        if len(row) > 1 and row[1]:
            name = str(row[1]).strip()
            if name and not name.startswith("#"):
                name_norm = normalize_name(name)
                name_positions[name_norm].append((row_idx - 2, 1, name))  # 0-indexed for API

        # Column C: Team Lead
        if len(row) > 2 and row[2]:
            name = str(row[2]).strip()
            if name and not name.startswith("#"):
                name_norm = normalize_name(name)
                name_positions[name_norm].append((row_idx - 2, 2, name))

        # Column G: Team Members
        if len(row) > 6 and row[6]:
            for member in str(row[6]).split(","):
                name = member.strip()
                if name and not name.startswith("#"):
                    name_norm = normalize_name(name)
                    name_positions[name_norm].append((row_idx - 2, 6, name))

    # Find all duplicates
    all_duplicate_cells = []
    for name_norm, positions in name_positions.items():
        if len(positions) > 1:
            # This name appears multiple times
            for row, col, actual_name in positions:
                all_duplicate_cells.append((row, col, actual_name, name_norm))

    print(f"    ✓ Found {len(all_duplicate_cells)} duplicate cells")

    # Separate by type
    junk_duplicates = []  # 0, 1, 2, 3, etc., —
    legitimate_duplicates = []

    junk_patterns = ["0", "1", "2", "3", "4", "5", "8", "9", "—"]

    for row, col, actual_name, name_norm in all_duplicate_cells:
        if actual_name in junk_patterns or actual_name.isdigit():
            junk_duplicates.append((row, col, actual_name))
        else:
            legitimate_duplicates.append((row, col, actual_name))

    print(f"    ✓ Junk duplicates: {len(junk_duplicates)}")
    print(f"    ✓ Legitimate duplicates: {len(legitimate_duplicates)}")

    # Create formatting requests for Google Sheets API
    services = get_google_services()
    sheets = services["sheets"]

    requests = []

    # Highlight JUNK duplicates in RED
    print("\n[3] Preparing to highlight junk data (RED)...")
    for row, col, name in junk_duplicates:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": int(TRACKER_GID),
                    "startRowIndex": row,
                    "endRowIndex": row + 1,
                    "startColumnIndex": col,
                    "endColumnIndex": col + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1, "green": 0.7, "blue": 0.7},  # Light red
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        })

    print(f"    ✓ Prepared {len(junk_duplicates)} red highlight requests")

    # Highlight LEGITIMATE duplicates in YELLOW
    print("\n[4] Preparing to highlight legitimate duplicates (YELLOW)...")
    for row, col, name in legitimate_duplicates:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": int(TRACKER_GID),
                    "startRowIndex": row,
                    "endRowIndex": row + 1,
                    "startColumnIndex": col,
                    "endColumnIndex": col + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1, "green": 1, "blue": 0.7},  # Light yellow
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        })

    print(f"    ✓ Prepared {len(legitimate_duplicates)} yellow highlight requests")

    # Apply all formatting in batches (API limit ~200 requests per batch)
    print("\n[5] Applying highlighting to sheet...")
    batch_size = 200
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=TRACKER_SHEET_ID,
            body={"requests": batch}
        ).execute()
        print(f"    ✓ Applied batch {i//batch_size + 1} ({len(batch)} requests)")

    print("\n" + "="*120)
    print("✓ HIGHLIGHTING COMPLETE!")
    print("="*120)
    print(f"\nHighlighting summary:")
    print(f"  🔴 RED (Junk data - 0, 1, 2, 3, etc., —): {len(junk_duplicates)} cells")
    print(f"  🟡 YELLOW (Legitimate duplicates - team leads): {len(legitimate_duplicates)} cells")
    print(f"  Total highlighted: {len(requests)} cells")
    print(f"\nSheet: https://docs.google.com/spreadsheets/d/{TRACKER_SHEET_ID}")
    print(f"\nNOTE:")
    print(f"  • RED cells = Junk/garbage data that should be removed")
    print(f"  • YELLOW cells = Team leads listed multiple times (expected)")

if __name__ == "__main__":
    main()
