#!/usr/bin/env python3
"""Count all employees in December 2024 onwards (all are OPL)"""

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

def count_all_employees(sheets_service, sheet_id, month_name):
    """Count all employees in a sheet (all are OPL)"""
    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"\nSheets in workbook: {len(sheets)}")
        for i, sheet in enumerate(sheets):
            title = sheet['properties']['title']
            print(f"  {i+1}. '{title}'")

        total_employees = 0
        all_names = {}  # Track unique employees across sheets

        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"\nReading: '{sheet_name}'")

            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"'{sheet_name}'!A1:Z1000"
            ).execute()

            rows = result.get('values', [])

            # Find header with employee info
            header_row = None
            for i, row in enumerate(rows[:15]):
                if row and any('employee' in str(cell).lower() or 'name' in str(cell).lower() for cell in row):
                    header_row = i
                    break

            if header_row is None:
                print(f"  No employee header found")
                continue

            headers = rows[header_row]
            name_col = None

            # Find name column
            for col_idx, header in enumerate(headers):
                h = str(header).lower()
                if ('employee' in h or 'name' in h) and name_col is None:
                    name_col = col_idx

            if name_col is None:
                print(f"  No name column found")
                continue

            # Count all employees - no filtering
            count = 0
            for row_idx in range(header_row + 1, len(rows)):
                row = rows[row_idx]
                if not row or len(row) <= name_col:
                    continue

                name = str(row[name_col]).strip() if name_col < len(row) else ''
                if not name:
                    continue

                # Only skip if it's clearly a total row
                if 'total' in name.lower():
                    continue

                # Count if name has at least some characters
                if len(name) >= 2:
                    count += 1
                    if name not in all_names:
                        all_names[name] = sheet_name

            print(f"  Employees in this sheet: {count}")
            total_employees += count

        # Return unique count (in case of duplicates across sheets)
        unique_count = len(all_names)
        return total_employees, unique_count

    except Exception as e:
        print(f"  Error: {e}")
        return 0, 0

def main():
    creds = load_credentials()
    if not creds:
        return

    sheets_service = build('sheets', 'v4', credentials=creds)

    # December 2024 sheet
    sheet_id = '1_A5o1Aln9AjEmjX-BzXyWfHdzLajYvwiRVmRtiKH4hs'

    print("="*120)
    print("DECEMBER 2024 - COUNTING ALL OPL EMPLOYEES")
    print("="*120)

    total, unique = count_all_employees(sheets_service, sheet_id, 'December 2024')

    print(f"\n{'='*120}")
    print(f"Total count (across all sheets): {total}")
    print(f"Unique employees: {unique}")
    print(f"{'='*120}")

if __name__ == '__main__':
    main()
