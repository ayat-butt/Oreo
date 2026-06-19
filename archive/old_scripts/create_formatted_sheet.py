#!/usr/bin/env python3
"""Create formatted Google Sheet from employee data."""

import os
import csv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

def get_sheet_service():
    """Get Google Sheets service with authentication."""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    token_path = '/c/Agent Oreo/token.json'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token_file:
            creds = pickle.load(token_file)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())

    if not creds:
        print("ERROR: Could not load credentials from token.json")
        print("Please ensure Google authentication is set up.")
        return None

    return build('sheets', 'v4', credentials=creds)

def read_csv(filepath):
    """Read CSV file and return as list of lists."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data

def create_spreadsheet(service, title):
    """Create a new Google Sheet."""
    try:
        spreadsheet = {
            'properties': {
                'title': title,
                'locale': 'en_PK',
                'autoRecalc': 'ON_CHANGE',
                'defaultFormat': {
                    'backgroundColor': {'red': 1, 'green': 1, 'blue': 1},
                    'padding': {'top': 2, 'right': 3, 'bottom': 2, 'left': 3},
                    'verticalAlignment': 'MIDDLE',
                    'wrapStrategy': 'OVERFLOW_CELL',
                    'textFormat': {'fontSize': 10, 'fontFamily': 'Calibri'}
                }
            },
            'sheets': [
                {
                    'properties': {
                        'sheetId': 0,
                        'title': 'Employees',
                        'gridProperties': {'rowCount': 1, 'columnCount': 14}
                    }
                },
                {
                    'properties': {
                        'sheetId': 1,
                        'title': 'Dependents',
                        'gridProperties': {'rowCount': 1, 'columnCount': 6}
                    }
                }
            ]
        }

        result = service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()

        return result
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def update_sheet_data(service, sheet_id, sheet_range, values):
    """Update sheet with data."""
    try:
        body = {'values': values}
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=sheet_range,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        return result
    except HttpError as error:
        print(f'Error updating sheet: {error}')
        return None

def format_header_row(service, sheet_id, sheet_id_int, num_columns):
    """Format header row with background color and bold text."""
    try:
        requests = [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id_int,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.6},
                            'textFormat': {
                                'bold': True,
                                'fontSize': 11,
                                'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                            },
                            'alignment': {
                                'horizontal': 'CENTER',
                                'vertical': 'MIDDLE'
                            }
                        }
                    },
                    'fields': 'userEnteredFormat'
                }
            },
            {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': sheet_id_int,
                        'gridProperties': {'frozenRowCount': 1}
                    },
                    'fields': 'gridProperties.frozenRowCount'
                }
            }
        ]

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={'requests': requests}
        ).execute()
    except HttpError as error:
        print(f'Error formatting: {error}')

def main():
    print("\n" + "=" * 80)
    print("CREATING FORMATTED GOOGLE SHEET")
    print("=" * 80)

    # Get service
    print("\nAuthententicating with Google Sheets API...")
    service = get_sheet_service()
    if not service:
        print("[ERROR] Failed to authenticate. Please check token.json")
        return

    print("[OK] Authenticated successfully")

    # Create spreadsheet
    print("\nCreating new spreadsheet...")
    title = f"Employee Profiles & Dependents - {datetime.now().strftime('%Y-%m-%d')}"
    result = create_spreadsheet(service, title)

    if not result:
        print("[ERROR] Failed to create spreadsheet")
        return

    sheet_id = result['spreadsheetId']
    sheet_url = result['spreadsheetUrl']
    print(f"[OK] Spreadsheet created: {sheet_id}")

    # Read employee data
    print("\nReading employee data...")
    emp_data = read_csv('/c/Agent Oreo/output/EMPLOYEES_PROFILES.csv')
    print(f"[OK] Loaded {len(emp_data)} rows (including header)")

    # Read dependent data
    print("Reading dependent data...")
    dep_data = read_csv('/c/Agent Oreo/output/EMPLOYEE_DEPENDENTS.csv')
    print(f"[OK] Loaded {len(dep_data)} rows (including header)")

    # Update employee sheet
    print("\nUpdating Employees sheet...")
    update_sheet_data(service, sheet_id, 'Employees!A1', emp_data)
    format_header_row(service, sheet_id, 0, len(emp_data[0]))
    print(f"[OK] Updated {len(emp_data)} rows")

    # Update dependent sheet
    print("Updating Dependents sheet...")
    update_sheet_data(service, sheet_id, 'Dependents!A1', dep_data)
    format_header_row(service, sheet_id, 1, len(dep_data[0]))
    print(f"[OK] Updated {len(dep_data)} rows")

    # Summary
    print("\n" + "=" * 80)
    print("SUCCESS - SHEET CREATED")
    print("=" * 80)
    print(f"\nSheet ID: {sheet_id}")
    print(f"URL: {sheet_url}")
    print(f"\nTotal Employees: {len(emp_data) - 1}")
    print(f"Total Dependents: {len(dep_data) - 1}")
    print("\nSheet contains:")
    print("  - Sheet 1: 'Employees' with 14 columns")
    print("  - Sheet 2: 'Dependents' with 6 columns")

if __name__ == "__main__":
    main()
