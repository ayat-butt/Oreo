#!/usr/bin/env python3
"""Check the comprehensive payroll sheets for addition/deletion data"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            import json
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except:
        return None

creds = load_credentials()
service = build('sheets', 'v4', credentials=creds)

# Comprehensive payroll sheet
spreadsheet_id = '1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k'

# Check metadata for all sheets
try:
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get('sheets', [])

    print("All sheets in comprehensive payroll:")
    for sheet in sheets:
        print(f"  - {sheet['properties']['title']}")

    # Now check if any sheet has addition/deletion data
    print("\n" + "="*150)
    print("Checking for EMPLOYEE ADDITION/DELETION sections")
    print("="*150)

    # Check November from comprehensive file
    print("\nChecking 'November 2024' tab for structure...")

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="'November 2024'!A1:H300"
    ).execute()

    rows = result.get('values', [])

    for i, row in enumerate(rows[:100]):
        if row and any('EMPLOYEE' in str(cell).upper() for cell in row):
            print(f"\nFound section at row {i}: {row}")
            # Print next 30 rows
            for j in range(i, min(i+30, len(rows))):
                print(f"  Row {j}: {rows[j]}")
            break

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
