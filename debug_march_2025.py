#!/usr/bin/env python3
"""Debug March 2025 sheet"""

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

    # March 2025 sheet
    sheet_id = '1ahND0ab4mIOe1_dduUt-2tuxKvdugoEyNd2qh8HV5TQ'

    print("="*120)
    print("DEBUGGING MARCH 2025 SHEET")
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

        print(f"\nReading each sheet (counting unique employees):\n")

        all_employees = {}  # name -> sheet_name
        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"  Sheet: '{sheet_name}'")

            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"'{sheet_name}'!A1:Z500"
            ).execute()

            rows = result.get('values', [])

            # Find header
            header_row = None
            for i, row in enumerate(rows[:15]):
                if row and any('employee' in str(cell).lower() or 'name' in str(cell).lower() for cell in row):
                    header_row = i
                    break

            if header_row is None:
                print(f"    No employee header found")
                continue

            headers = rows[header_row]
            name_col = None

            # Find name column
            for col_idx, header in enumerate(headers):
                h = str(header).lower()
                if ('employee' in h or 'name' in h) and name_col is None:
                    name_col = col_idx

            if name_col is None:
                print(f"    No name column found")
                continue

            # Count employees
            count = 0
            for row_idx in range(header_row + 1, len(rows)):
                row = rows[row_idx]
                if not row or len(row) <= name_col:
                    continue

                name = str(row[name_col]).strip() if name_col < len(row) else ''
                if not name or 'total' in name.lower() or len(name) < 3:
                    continue

                count += 1
                if name not in all_employees:
                    all_employees[name] = sheet_name

            print(f"    Found {count} employees")
            print()

        print(f"Unique employees across all sheets: {len(all_employees)}")
        print(f"\nEmployee names with their sheets:")
        for name in sorted(all_employees.keys())[:20]:
            print(f"  {name} -> {all_employees[name]}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
