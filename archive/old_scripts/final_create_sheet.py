#!/usr/bin/env python3
"""Create and populate Google Sheet with employee data."""

import os
import json
import csv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from datetime import datetime

def load_credentials():
    """Load Google credentials from token.json."""
    token_path = 'c:/Agent Oreo/token.json'

    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)

        # Create credentials from token data
        creds = Credentials.from_authorized_user_info(token_data)

        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return creds
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def read_csv(filepath):
    """Read CSV file."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data

def create_and_populate_sheet():
    """Create Google Sheet and populate with data."""

    # Load credentials
    print("Loading Google credentials...")
    creds = load_credentials()
    if not creds:
        print("[ERROR] Could not load credentials")
        return None

    # Build service
    service = build('sheets', 'v4', credentials=creds)

    # Read data
    print("Reading employee data...")
    emp_data = read_csv('c:/Agent Oreo/output/EMPLOYEES_PROFILES.csv')
    print(f"  Loaded {len(emp_data)} employee records")

    print("Reading dependent data...")
    dep_data = read_csv('c:/Agent Oreo/output/EMPLOYEE_DEPENDENTS.csv')
    print(f"  Loaded {len(dep_data)} dependent records")

    # Create spreadsheet
    print("\nCreating Google Sheet...")
    title = f"Employee Profiles & Dependents - {datetime.now().strftime('%Y-%m-%d')}"

    spreadsheet = {
        'properties': {'title': title}
    }

    result = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
    sheet_id = result['spreadsheetId']
    sheet_url = result['spreadsheetUrl']

    print(f"[OK] Sheet created")
    print(f"Sheet ID: {sheet_id}")

    # Rename and create sheets
    print("\nSetting up sheets...")
    requests = [
        {
            'updateSheetProperties': {
                'properties': {
                    'sheetId': 0,
                    'title': 'Employees'
                },
                'fields': 'title'
            }
        }
    ]

    service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': requests}).execute()

    # Add second sheet
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={
            'requests': [
                {
                    'addSheet': {
                        'properties': {'title': 'Dependents'}
                    }
                }
            ]
        }
    ).execute()

    # Update employee sheet
    print("Populating Employees sheet...")
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Employees!A1',
        valueInputOption='USER_ENTERED',
        body={'values': emp_data}
    ).execute()

    # Update dependents sheet
    print("Populating Dependents sheet...")
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Dependents!A1',
        valueInputOption='USER_ENTERED',
        body={'values': dep_data}
    ).execute()

    # Format headers
    print("Formatting headers...")
    requests = [
        {
            'repeatCell': {
                'range': {
                    'sheetId': 0,
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
                        }
                    }
                },
                'fields': 'userEnteredFormat'
            }
        },
        {
            'repeatCell': {
                'range': {
                    'sheetId': 1,
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
                        }
                    }
                },
                'fields': 'userEnteredFormat'
            }
        }
    ]

    service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': requests}).execute()

    return {
        'sheet_id': sheet_id,
        'sheet_url': sheet_url,
        'title': title,
        'employees': len(emp_data) - 1,
        'dependents': len(dep_data) - 1
    }

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CREATING GOOGLE SHEET WITH EMPLOYEE DATA")
    print("=" * 80 + "\n")

    result = create_and_populate_sheet()

    if result:
        print("\n" + "=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print(f"\nSheet URL: {result['sheet_url']}")
        print(f"Sheet ID: {result['sheet_id']}")
        print(f"\nTitle: {result['title']}")
        print(f"Employees: {result['employees']}")
        print(f"Dependents: {result['dependents']}")

        # Save to file
        with open('c:/Agent Oreo/output/sheet_link.txt', 'w') as f:
            f.write(f"Sheet URL: {result['sheet_url']}\n")
            f.write(f"Sheet ID: {result['sheet_id']}\n")

        print("\nSheet link saved to output/sheet_link.txt")
    else:
        print("\n[ERROR] Failed to create sheet")
