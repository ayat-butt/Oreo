#!/usr/bin/env python3
"""Extract bank details from March 2026 Payroll sheet."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def load_google_credentials():
    token_path = 'c:/Agent Oreo/token.json'
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    payroll_sheet_id = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'

    print("Reading Payroll Sheet structure...\n")

    # Get sheet metadata to find the March 2026 tab
    try:
        metadata = service.spreadsheets().get(spreadsheetId=payroll_sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print("Available sheets in Payroll file:")
        for sheet in sheets:
            title = sheet['properties']['title']
            sheet_id = sheet['properties']['sheetId']
            print(f"  - {title} (ID: {sheet_id})")

        # Look for March 2026 sheet
        march_sheet = None
        for sheet in sheets:
            if '2026' in sheet['properties']['title'] or 'march' in sheet['properties']['title'].lower():
                march_sheet = sheet['properties']['title']
                break

        if not march_sheet:
            march_sheet = 'MARCH 2026'  # Try default name

        print(f"\nReading data from: {march_sheet}")

        # Get headers and sample data
        result = service.spreadsheets().values().get(
            spreadsheetId=payroll_sheet_id,
            range=f"'{march_sheet}'!A1:Z10"
        ).execute()

        values = result.get('values', [])

        print("\nPayroll Sheet Structure (First 10 rows):")
        print("-" * 150)

        # Show headers
        if values:
            headers = values[0] if values[0] else []
            print(f"\nHeaders ({len(headers)} columns):")
            for idx, header in enumerate(headers):
                print(f"  Col {idx}: {header}")

            # Show sample rows
            print(f"\nSample Data (rows 1-3):")
            for row_idx, row in enumerate(values[1:4], 1):
                print(f"\nRow {row_idx}:")
                for col_idx, cell in enumerate(row[:15]):  # Show first 15 columns
                    try:
                        print(f"  Col {col_idx}: {cell}")
                    except:
                        print(f"  Col {col_idx}: [Non-ASCII]")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
