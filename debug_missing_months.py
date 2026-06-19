#!/usr/bin/env python3
"""Debug missing months (Feb, Apr, Jun 2025) to verify OPL data exists"""

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

def check_month_data(service, month, sheet_id):
    """Debug a specific month to understand data structure"""
    print(f"\n{'='*100}")
    print(f"DEBUGGING: {month}")
    print(f"Sheet ID: {sheet_id}")
    print(f"{'='*100}")

    try:
        # Get metadata
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"\nSheets found: {len(sheets)}")
        for sheet in sheets:
            title = sheet['properties']['title']
            print(f"  - {title}")

        # Try each sheet
        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"\nTrying sheet: '{sheet_name}'")

            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=sheet_id,
                    range=f"'{sheet_name}'!A1:Z500"
                ).execute()

                rows = result.get('values', [])
                print(f"  Total rows: {len(rows)}")

                if not rows:
                    print(f"  Status: EMPTY")
                    continue

                # Show first 10 rows
                print(f"  First 10 rows:")
                for i, row in enumerate(rows[:10]):
                    print(f"    Row {i}: {row}")

                # Find header
                header_row = None
                for i, row in enumerate(rows[:15]):
                    if row and any('employee' in str(cell).lower() for cell in row):
                        header_row = i
                        break

                if header_row is None:
                    print(f"  No employee header found")
                    continue

                print(f"  Header row: {header_row}")
                print(f"  Headers: {rows[header_row]}")

                # Count employees
                emp_count = 0
                for row_idx in range(header_row + 1, len(rows)):
                    row = rows[row_idx]
                    if row and len(row) > 0:
                        name = row[0].strip() if row else ''
                        if name and 'total' not in name.lower() and len(name) >= 3:
                            emp_count += 1

                print(f"  Employee records found: {emp_count}")

            except Exception as e:
                print(f"  Error reading sheet: {str(e)[:100]}")
                continue

    except Exception as e:
        print(f"Error: {e}")

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    service = build('sheets', 'v4', credentials=creds)

    # Check problematic months
    problematic_sheets = {
        'February 2025': '1T5rMIo0Apv41Tm-jDstU1qT5Lp6raFGhBNaYPIR4oe0',
        'April 2025': '1lOSgTwzvI0NudWB6voUXJaNhViAqBbCPhCURqTZQx8k',
        'June 2025': '1KtM9hkNIFEnvYWO8DFZf1iVSZungdiWdIGAsQTmu-Us',
    }

    for month, sheet_id in problematic_sheets.items():
        check_month_data(service, month, sheet_id)

if __name__ == '__main__':
    main()
