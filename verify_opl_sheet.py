#!/usr/bin/env python3
"""Verify the created OPL sheet format"""

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

creds = load_credentials()
service = build('sheets', 'v4', credentials=creds)

# The newly created sheet
sheet_id = '1gSCNdfIRMf5NyaT_WvDrI2J1SwTydlj8MSuZlL-z4yU'

try:
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Sheet1!A1:G30'
    ).execute()
    
    rows = result.get('values', [])
    
    print("OPL Sheet - First 30 rows:")
    print("="*150)
    
    for i, row in enumerate(rows[:30], 1):
        # Format for display
        display_row = []
        for cell in row:
            display_row.append(str(cell)[:30])  # Limit to 30 chars for display
        print(f"Row {i:2d}: {' | '.join(display_row)}")
    
    print("\n" + "="*150)
    print(f"\nTotal rows: {len(rows)}")
    print(f"\nVerification:")
    print(f"  Row 1: Empty column A + title")
    print(f"  Row 2: Header row")
    print(f"  Rows 3+: Employee data")
    
    # Count employees (exclude header rows)
    employee_count = len(rows) - 3  # Exclude first 3 rows (blank, title, header)
    print(f"\nTotal employees in sheet: {employee_count}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
