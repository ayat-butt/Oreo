#!/usr/bin/env python3
"""
Create final clean tracker by:
1. Removing rows 144-198 (junk data)
2. Consolidating duplicate entries
3. Keeping 91 unique employees with clean structure
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from collections import defaultdict
from hr_assistant.config import get_google_services

TRACKER_SHEET_ID = "1qiFuYR95rxHhErb-zDCZZ5B9D4fCEKbLdCB-3xI4QJI"
TRACKER_GID = "654305400"

def read_tracker_sheet():
    """Read current tracker sheet."""
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

def normalize_name(name):
    """Normalize name."""
    return name.lower().strip().replace("  ", " ")

def main():
    print("="*120)
    print("CREATING CLEAN FINAL TRACKER")
    print("="*120)

    print("\n[1] Reading tracker...")
    rows, sheet_name = read_tracker_sheet()
    print(f"    ✓ {len(rows)} total rows")

    print("\n[2] Removing junk rows (144-198)...")
    # Keep only rows 1-143 (header + first 142 data rows)
    clean_rows = rows[:143]
    print(f"    ✓ Removed {len(rows) - len(clean_rows)} junk rows")
    print(f"    ✓ Keeping {len(clean_rows)} rows")

    print("\n[3] Identifying duplicate team leads...")

    # Track team leads and their subordinates
    team_lead_data = defaultdict(lambda: {"depts": set(), "reports_to": set(), "levels": set(), "all_members": set(), "row_nums": []})

    for row_idx, row in enumerate(clean_rows[1:], start=2):
        if len(row) < 7:
            continue

        dept = row[0] if row[0] else "—"
        team_lead = row[2] if len(row) > 2 and row[2] else None
        reports_to = row[3] if len(row) > 3 and row[3] else None
        level = row[4] if len(row) > 4 and row[4] else "—"
        team_members = row[6] if len(row) > 6 and row[6] else None

        if team_lead and str(team_lead).strip():
            tl_norm = normalize_name(str(team_lead))
            team_lead_data[tl_norm]["depts"].add(dept)
            team_lead_data[tl_norm]["reports_to"].add(reports_to)
            team_lead_data[tl_norm]["levels"].add(level)
            team_lead_data[tl_norm]["row_nums"].append(row_idx)

            if team_members:
                for member in str(team_members).split(","):
                    member = member.strip()
                    if member and member != "—":
                        team_lead_data[tl_norm]["all_members"].add(member)

    duplicates = {name: data for name, data in team_lead_data.items() if len(data["row_nums"]) > 1}

    print(f"    ✓ Found {len(duplicates)} team leads appearing multiple times")
    print(f"    ✓ They manage {sum(len(d['all_members']) for d in duplicates.values())} total subordinates")

    if duplicates:
        print(f"\n    Duplicates found:")
        for name_norm, data in sorted(duplicates.items()):
            # Use the actual name from a team lead row
            actual_name = None
            for row_idx in data["row_nums"]:
                tl = clean_rows[row_idx][2] if len(clean_rows[row_idx]) > 2 else None
                if tl and normalize_name(str(tl)) == name_norm:
                    actual_name = str(tl)
                    break

            print(f"      • {actual_name}: {len(data['row_nums'])} rows, {len(data['all_members'])} subordinates")

    print("\n[4] Creating consolidated tracker...")

    # Build new rows by consolidating duplicates
    new_rows = [clean_rows[0]]  # Keep header

    processed_names = set()

    for row_idx, row in enumerate(clean_rows[1:], start=2):
        if len(row) < 7:
            continue

        team_lead = row[2] if len(row) > 2 and row[2] else None

        if team_lead and str(team_lead).strip():
            tl_norm = normalize_name(str(team_lead))

            # Only add once per unique team lead
            if tl_norm not in processed_names:
                # Add the row as-is
                new_rows.append(row)
                processed_names.add(tl_norm)
                # Skip any subsequent rows with the same team lead
            # else: skip duplicate rows
        else:
            # Non-team lead rows (individual contributors), keep all
            new_rows.append(row)

    print(f"    ✓ Original data rows: {len(clean_rows) - 1}")
    print(f"    ✓ After consolidation: {len(new_rows) - 1}")
    print(f"    ✓ Rows removed: {len(clean_rows) - len(new_rows)}")

    print("\n[5] Updating Google Sheet...")
    services = get_google_services()
    sheets = services["sheets"]

    # Clear
    sheets.spreadsheets().values().clear(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'{sheet_name}'!A1:Z500"
    ).execute()

    # Write
    sheets.spreadsheets().values().update(
        spreadsheetId=TRACKER_SHEET_ID,
        range=f"'{sheet_name}'!A1",
        valueInputOption="RAW",
        body={"values": new_rows},
    ).execute()

    print(f"    ✓ Sheet updated with {len(new_rows)} rows")

    # Format header
    print("\n[6] Formatting...")
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=TRACKER_SHEET_ID,
        body={"requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": int(TRACKER_GID),
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.7},
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
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": int(TRACKER_GID),
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 7,
                    }
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": int(TRACKER_GID),
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]},
    ).execute()

    print("    ✓ Formatted")

    print("\n" + "="*120)
    print("✓ CLEAN TRACKER CREATED!")
    print("="*120)
    print(f"\nFinal Statistics:")
    print(f"  • Total rows (including header): {len(new_rows)}")
    print(f"  • Total employees: {len(new_rows) - 1}")
    print(f"  • Rows removed: {len(clean_rows) - len(new_rows)} (junk + duplicates)")
    print(f"  • Rows kept: {len(new_rows) - 1}")
    print(f"\nStructure:")
    print(f"  Department | SMT | Team Lead | Reports To | Level | Team Member | # Members")
    print(f"\nSheet: https://docs.google.com/spreadsheets/d/{TRACKER_SHEET_ID}")

if __name__ == "__main__":
    main()
