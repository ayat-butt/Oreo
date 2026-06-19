#!/usr/bin/env python3
"""Update probation tracker sheet based on Gmail evidence."""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services
from datetime import datetime

SHEET_ID = "1_yvL_lM3WzE5BBzsk60PO7gutsYer_y1PSFbTT0hJBY"
GID = "322356645"

def main():
    services = get_google_services()
    sheets = services["sheets"]

    # Get sheet metadata
    metadata = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == GID:
            sheet_name = sheet["properties"]["title"]
            break

    print("=" * 120)
    print("UPDATING PROBATION TRACKER SHEET")
    print("=" * 120)
    print(f"\nSheet: {sheet_name}")

    # Read current data
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1:M100"
    ).execute()

    rows = result.get("values", [])

    # Find header row
    header_row = None
    for i, row in enumerate(rows):
        if row and "#" in str(row[0]) and "Name" in str(row):
            header_row = i
            break

    print(f"Header row: {header_row + 1}")

    # Map column indices
    col_map = {}
    headers = rows[header_row]
    for i, h in enumerate(headers):
        col_map[h] = i

    print(f"Column mapping: Name={col_map.get('Name')}, Closure Status={col_map.get('Probation Closure Status')}")

    # Updates to make
    updates = [
        {
            "name": "Taloot Ahmad Malik",
            "closure_status": "Completed — Apr 10",
            "gmail_evidence": "Apr 10: Probation Completion Confirmation"
        },
        {
            "name": "M. Saim",
            "closure_status": "Completed — Apr 08",
            "gmail_evidence": "Apr 8: Successfully completed probation"
        },
        {
            "name": "Samra Tariq",
            "closure_status": "Completed — Apr 08",
            "gmail_evidence": "Apr 8: Probation Assessment Summary sent"
        }
    ]

    # Find and update rows
    update_requests = []
    name_col = col_map.get("Name")
    closure_col = col_map.get("Probation Closure Status")
    req_col = col_map.get("Requirement")

    for update in updates:
        # Find the row with this employee
        for i in range(header_row + 1, len(rows)):
            row = rows[i]
            if len(row) > name_col and row[name_col] == update["name"]:
                print(f"\nFound: {update['name']} at row {i + 1}")
                print(f"  Current closure status: {row[closure_col] if closure_col < len(row) else 'N/A'}")
                print(f"  Gmail evidence: {update['gmail_evidence']}")
                print(f"  New closure status: {update['closure_status']}")

                # Prepare update
                cell_ref = f"'{sheet_name}'!{chr(65 + closure_col)}{i + 1}"
                update_requests.append({
                    "range": cell_ref,
                    "values": [[update["closure_status"]]]
                })

                # Also update Requirement to "Not Needed" if closure is completed
                if "Completed" in update["closure_status"]:
                    req_cell_ref = f"'{sheet_name}'!{chr(65 + req_col)}{i + 1}"
                    update_requests.append({
                        "range": req_cell_ref,
                        "values": [["Not Needed"]]
                    })
                break

    # Execute batch update
    if update_requests:
        print(f"\n[Batch Update] Updating {len(update_requests)} cells...")

        batch_body = {
            "data": update_requests,
            "valueInputOption": "RAW"
        }

        response = sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body=batch_body
        ).execute()

        print(f"Updates applied: {response.get('updatedCells')} cells updated")
        print(f"Updated ranges: {len(response.get('responses', []))} range(s)")

        print("\n" + "=" * 120)
        print("SHEET UPDATE COMPLETED")
        print("=" * 120)
        print("\nUpdated employees:")
        for i, update in enumerate(updates, 1):
            print(f"  {i}. {update['name']}")
            print(f"     New Status: {update['closure_status']}")
            print(f"     Evidence: {update['gmail_evidence']}")
        print("\n" + "=" * 120)
    else:
        print("No matching rows found to update")

if __name__ == "__main__":
    main()
