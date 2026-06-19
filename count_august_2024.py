#!/usr/bin/env python3
"""Count all employees in August 2024 sheet (all are OPL)"""

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
    print("AUGUST 2024 - COUNT ALL EMPLOYEES (ALL ARE OPL)")
    print("="*120)

    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"\nSheets in workbook: {len(sheets)}")
        for i, sheet in enumerate(sheets):
            title = sheet['properties']['title']
            print(f"  {i+1}. '{title}'")

        total_employees = 0

        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"\nReading sheet: '{sheet_name}'")

            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"'{sheet_name}'!A1:Z1000"
            ).execute()

            rows = result.get('values', [])
            print(f"  Total rows: {len(rows)}")

            # Find header with employee info
            header_row = None
            for i, row in enumerate(rows[:15]):
                if row and any('employee' in str(cell).lower() or 'name' in str(cell).lower() for cell in row):
                    header_row = i
                    break

            if header_row is None:
                print(f"  No employee header found")
                continue

            print(f"  Header row: {header_row}")
            headers = rows[header_row]
            print(f"  Headers: {headers}")

            # Find name column
            name_col = None
            for col_idx, header in enumerate(headers):
                h = str(header).lower()
                if ('employee' in h or 'name' in h) and name_col is None:
                    name_col = col_idx

            if name_col is None:
                print(f"  No name column found")
                continue

            print(f"  Name column index: {name_col}")

            # Count valid employees
            count = 0
            for row_idx in range(header_row + 1, len(rows)):
                row = rows[row_idx]
                if not row or len(row) <= name_col:
                    continue

                name = str(row[name_col]).strip() if name_col < len(row) else ''
                if not name or 'total' in name.lower() or len(name) < 3:
                    continue

                count += 1

            print(f"  Employees in this sheet: {count}")
            total_employees += count

        print(f"\n{'='*120}")
        print(f"TOTAL OPL EMPLOYEES IN AUGUST 2024: {total_employees}")
        print(f"{'='*120}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
