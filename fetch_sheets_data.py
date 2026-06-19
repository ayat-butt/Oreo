#!/usr/bin/env python3
"""
Fetch spreadsheet data using Google Sheets API v4.
Follows the approach verified to work by colleague.
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

def load_credentials():
    """Load stored Google OAuth token."""
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        # Refresh token if needed
        if creds.expired:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def main():
    # Step 1: Load credentials
    print("Step 1: Loading credentials...")
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    # Step 2: Build Sheets API client
    print("Step 2: Building Sheets API client...")
    service = build('sheets', 'v4', credentials=creds)

    # Step 3: Fetch spreadsheet metadata
    spreadsheet_id = '1otyZycsDSJWjo59vacxT6lbYMmroc3BniJz4micUNXY'
    print(f"Step 3: Fetching metadata for spreadsheet {spreadsheet_id}...")

    try:
        metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = metadata.get('sheets', [])
        print(f"\nFound {len(sheets)} tabs:")
        for i, sheet in enumerate(sheets):
            print(f"  {i+1}. {sheet['properties']['title']}")

        # Step 4-7: Read data from each tab
        print("\n" + "="*60)
        for sheet in sheets:
            tab_name = sheet['properties']['title']
            sheet_id = sheet['properties']['sheetId']
            print(f"\nProcessing tab: {tab_name}")
            print("-" * 60)

            # Read header row (A1:Z1)
            header_range = f"'{tab_name}'!A1:Z1"
            header_result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=header_range
            ).execute()
            headers = header_result.get('values', [])
            if headers:
                print(f"Headers: {headers[0]}")

            # Read first 5 rows to understand structure
            sample_range = f"'{tab_name}'!A1:Z5"
            sample_result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sample_range
            ).execute()
            sample_data = sample_result.get('values', [])
            print(f"Sample data (first 5 rows):")
            for row in sample_data[:5]:
                print(f"  {row}")

            # Count employees (assuming column A has employee names)
            data_range = f"'{tab_name}'!A2:B1000"  # Skip header
            data_result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=data_range
            ).execute()
            data_rows = data_result.get('values', [])

            # Count non-empty name rows
            employee_count = 0
            for row in data_rows:
                if row and len(row) > 0 and row[0].strip():  # Non-empty name
                    employee_count += 1

            print(f"Employee count: {employee_count}")

            # If count is low, show all data
            if employee_count <= 5:
                print(f"Low count detected. Full data:")
                for row in data_rows:
                    if row:
                        print(f"  {row}")

        print("\n" + "="*60)
        print("Data fetch complete!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
