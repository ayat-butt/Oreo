#!/usr/bin/env python3
"""Debug November 2024 sheet to understand structure"""

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

    # November 2024 sheet
    sheet_id = '1wdTogupsdtkcOEXgQWNwsiJNnUOwx-87JYcpv6MSop4'

    print("="*120)
    print("DEBUGGING NOVEMBER 2024 SHEET")
    print("="*120)

    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"\nSheets in workbook: {len(sheets)}")
        for sheet in sheets:
            print(f"  - {sheet['properties']['title']}")

        # Read first sheet in detail
        if sheets:
            sheet_name = sheets[0]['properties']['title']
            print(f"\nReading first sheet: '{sheet_name}'")
            print("-" * 120)

            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"'{sheet_name}'!A1:Z100"
            ).execute()

            rows = result.get('values', [])
            print(f"Total rows: {len(rows)}")

            # Show headers
            if len(rows) > 0:
                print(f"\nFirst 15 rows (to find headers):")
                for i, row in enumerate(rows[:15]):
                    print(f"  Row {i}: {row[:10]}")  # Show first 10 columns

            # Find employee and entity columns
            header_row = None
            for i, row in enumerate(rows[:15]):
                if row and any('employee' in str(cell).lower() for cell in row):
                    header_row = i
                    break

            if header_row is not None:
                print(f"\nHeader row found at index {header_row}")
                headers = rows[header_row]
                print(f"All headers: {headers}")

                # Find entity-related columns
                print(f"\nLooking for entity/grade/company columns:")
                for col_idx, header in enumerate(headers):
                    h = str(header).lower()
                    if any(x in h for x in ['grade', 'entity', 'company', 'orenda', 'opl', 'division']):
                        print(f"  Column {col_idx}: '{header}'")

                # Show sample data
                print(f"\nFirst 10 employees with all columns:")
                name_col = None
                for col_idx, header in enumerate(headers):
                    if 'employee' in str(header).lower() and name_col is None:
                        name_col = col_idx

                if name_col is not None:
                    for row_idx in range(header_row + 1, min(header_row + 11, len(rows))):
                        row = rows[row_idx]
                        if row and len(row) > name_col:
                            name = str(row[name_col]).strip() if name_col < len(row) else ''
                            if name and 'total' not in name.lower() and len(name) > 2:
                                print(f"\n  {name}:")
                                for col_idx, header in enumerate(headers[:15]):
                                    val = str(row[col_idx]).strip() if col_idx < len(row) else ''
                                    if val:
                                        print(f"    {header}: {val}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
