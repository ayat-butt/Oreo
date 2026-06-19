#!/usr/bin/env python3
"""Create reference tab with old sheet data in the insurance sheet."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def load_google_credentials():
    """Load Google credentials."""
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

def read_old_sheet():
    """Read old insurance sheet."""
    print("Reading old insurance sheet...")
    creds = load_google_credentials()
    if not creds:
        return None

    service = build('sheets', 'v4', credentials=creds)
    old_sheet_id = '1HjyeoWzsxkC_t2yzPgSn6qb_huvNYq7qvzHB2m-AxHI'

    try:
        metadata = service.spreadsheets().get(spreadsheetId=old_sheet_id).execute()
        sheets = metadata.get('sheets', [])

        sheet_name = None
        for sheet in sheets:
            if sheet['properties']['sheetId'] == 195402472:
                sheet_name = sheet['properties']['title']
                break

        if not sheet_name:
            sheet_name = sheets[0]['properties']['title']

        result = service.spreadsheets().values().get(
            spreadsheetId=old_sheet_id,
            range=f'{sheet_name}'
        ).execute()

        return result.get('values', [])
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def parse_old_data(values):
    """Parse old sheet data."""
    if not values or len(values) < 2:
        return []

    data = []
    headers = values[0]

    for row_idx, row in enumerate(values[1:], 1):
        if not row or len(row) < 2:
            continue

        emp_name = row[0].strip() if row[0] else ""
        cnic = row[1].strip() if len(row) > 1 and row[1] else ""
        insured_name = row[2].strip() if len(row) > 2 and row[2] else ""
        relation = row[3].strip() if len(row) > 3 and row[3] else ""
        dob = row[4].strip() if len(row) > 4 and row[4] else ""
        health_plan = row[5].strip() if len(row) > 5 and row[5] else ""
        life_plan = row[6].strip() if len(row) > 6 and row[6] else ""
        opd_plan = row[7].strip() if len(row) > 7 and row[7] else ""
        date_added = row[9].strip() if len(row) > 9 and row[9] else ""

        if emp_name:
            data.append([
                emp_name,
                cnic,
                insured_name,
                relation,
                dob,
                health_plan,
                life_plan,
                opd_plan,
                date_added
            ])

    return data

def create_reference_tab_in_sheet(sheet_id, old_data):
    """Create reference tab in current insurance sheet."""
    print(f"Creating reference tab in current sheet...")

    creds = load_google_credentials()
    if not creds:
        return False

    service = build('sheets', 'v4', credentials=creds)

    try:
        # Add new sheet
        requests = [{
            'addSheet': {
                'properties': {
                    'title': 'Data from Old Insurance Sheet'
                }
            }
        }]

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={'requests': requests}
        ).execute()

        print("[OK] New tab created: 'Data from Old Insurance Sheet'")

        # Prepare headers and data
        headers = [
            'Employee Name (From Old Sheet)',
            'CNIC (From Old Sheet)',
            'Dependent/Insured Name',
            'Relationship',
            'DOB (Dependent)',
            'Health Insurance Plan',
            'Life Insurance Plan',
            'OPD Plan',
            'Date of Addition',
            'Status/Notes'
        ]

        data = [headers]

        # Add all old sheet data
        for row_data in old_data:
            row_with_status = row_data + ['']  # Add empty status column
            data.append(row_with_status)

        # Write data to new sheet
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A1",
            valueInputOption='USER_ENTERED',
            body={'values': data}
        ).execute()

        print(f"[OK] Added {len(old_data)} rows from old insurance sheet")

        # Get the new sheet ID
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        new_sheet_id = None
        for sheet in metadata.get('sheets', []):
            if sheet['properties']['title'] == 'Data from Old Insurance Sheet':
                new_sheet_id = sheet['properties']['sheetId']
                break

        if new_sheet_id is not None:
            # Format header
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': new_sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.8, 'green': 0.6, 'blue': 0.2},
                                'textFormat': {
                                    'bold': True,
                                    'fontSize': 11,
                                    'foregroundColor': {'red': 0, 'green': 0, 'blue': 0}
                                },
                                'horizontalAlignment': 'CENTER'
                            }
                        },
                        'fields': 'userEnteredFormat'
                    }
                },
                {
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': new_sheet_id,
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

            print("[OK] Header formatted and frozen")

            # Auto-resize columns
            requests = [{
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': new_sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 10
                    }
                }
            }]

            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': requests}
            ).execute()

            print("[OK] Columns auto-resized")
        else:
            print("[WARN] Could not format - will format manually")

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "=" * 100)
    print("CREATING REFERENCE TAB FROM OLD INSURANCE SHEET")
    print("=" * 100 + "\n")

    # Read old sheet
    old_values = read_old_sheet()
    if not old_values:
        print("[ERROR] Could not read old sheet")
        return

    print(f"[OK] Read {len(old_values)} rows from old sheet\n")

    # Parse data
    print("Parsing old sheet data...")
    old_data = parse_old_data(old_values)
    print(f"[OK] Parsed {len(old_data)} records\n")

    # Create reference tab
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'
    if create_reference_tab_in_sheet(sheet_id, old_data):
        print("\n" + "=" * 100)
        print("SUCCESS!")
        print("=" * 100)
        print("\nReference tab 'Data from Old Insurance Sheet' has been created!")
        print(f"Total records from old sheet: {len(old_data)}")
        print("\nSheet Structure:")
        print("  TAB 1: Main Sheet (Insurance - All Active Employees)")
        print("         └─ 246 active employees organized by entity & name")
        print("  TAB 2: Data from Old Insurance Sheet (REFERENCE)")
        print("         └─ All 160+ records from previous year's insurance")
        print("\nYou can now:")
        print("  1. Review old data in the reference tab")
        print("  2. Cross-check with main sheet")
        print("  3. Manually add missing data to main sheet where needed")
        print("  4. Use for filling CNICs, DOBs, or other details")
    else:
        print("[ERROR] Could not create reference tab")

if __name__ == "__main__":
    main()
