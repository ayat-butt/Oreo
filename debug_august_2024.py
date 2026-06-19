#!/usr/bin/env python3
"""Debug August 2024 sheet"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except:
        return None

def main():
    creds = load_credentials()
    if not creds:
        return

    sheets_service = build('sheets', 'v4', credentials=creds)

    # August 2024 sheet
    sheet_id = '1jBlbB-Ff54udES4o_G_-qhB8aAuW53Hb1jRlGNDmZ3E'

    print("="*120)
    print("DEBUGGING AUGUST 2024 SHEET")
    print("="*120)

    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"\nSheets in workbook: {len(sheets)}")
        for i, sheet in enumerate(sheets):
            title = sheet['properties']['title']
            grid_props = sheet['properties'].get('gridProperties', {})
            row_count = grid_props.get('rowCount', 0)
            print(f"  {i+1}. '{title}' ({row_count} rows)")

        print(f"\nReading each sheet:\n")

        total_opl = 0
        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"  Sheet: '{sheet_name}'")

            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"'{sheet_name}'!A1:Z100"
            ).execute()

            rows = result.get('values', [])

            # Find header
            header_row = None
            for i, row in enumerate(rows[:15]):
                if row and any('employee' in str(cell).lower() for cell in row):
                    header_row = i
                    break

            if header_row is None:
                print(f"    No employee header found")
                continue

            headers = rows[header_row]
            name_col = None
            entity_col = None

            # Find columns
            for col_idx, header in enumerate(headers):
                h = str(header).lower()
                if 'employee' in h and name_col is None:
                    name_col = col_idx
                elif any(x in h for x in ['grade', 'entity', 'company']):
                    entity_col = col_idx

            print(f"    Headers: {headers[:12]}")
            print(f"    Name column: {name_col}, Entity column: {entity_col}")

            # Count employees
            total = 0
            opl = 0
            for row_idx in range(header_row + 1, len(rows)):
                row = rows[row_idx]
                if not row or len(row) <= name_col:
                    continue

                name = str(row[name_col]).strip() if name_col < len(row) else ''
                if not name or 'total' in name.lower() or len(name) < 3:
                    continue

                total += 1

                if entity_col and entity_col < len(row):
                    entity = str(row[entity_col]).strip() if entity_col < len(row) else ''
                    if 'Orenda' in entity or 'OPL' in entity:
                        opl += 1
                        if opl <= 3:
                            print(f"      OPL: {name} | Entity: {entity}")

            print(f"    Total employees: {total}")
            print(f"    OPL employees: {opl}")
            total_opl += opl
            print()

        print(f"\nTotal OPL across all sheets: {total_opl}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
