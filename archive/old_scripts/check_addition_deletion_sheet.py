#!/usr/bin/env python3
"""Check Addition/Deletion sheet for Insurance."""

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
    
    addition_deletion_sheet_id = '18x6R4Gl3P_D-Dn_HHtLpXbpwQnqVafO6rekvovcVICk'

    print("Reading Addition/Deletion sheet...\n")

    try:
        # Get metadata to see all sheets
        metadata = service.spreadsheets().get(spreadsheetId=addition_deletion_sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print("Available sheets:")
        for sheet in sheets:
            title = sheet['properties']['title']
            sheet_id = sheet['properties']['sheetId']
            print(f"  - {title} (ID: {sheet_id})")

        print("\nReading data from sheets...\n")

        # Read all sheets to find additions and deletions
        for sheet in sheets:
            title = sheet['properties']['title']
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=addition_deletion_sheet_id,
                    range=f"'{title}'!A1:D50"
                ).execute()

                values = result.get('values', [])
                
                if values:
                    print(f"\n{'='*130}")
                    print(f"Sheet: {title}")
                    print(f"{'='*130}\n")
                    
                    # Show headers
                    if values:
                        headers = values[0]
                        print(f"Columns: {', '.join(headers)}\n")
                    
                    # Show first 20 rows
                    print(f"Data (first 20 rows):\n")
                    print(f"{'No':<5} {headers[0] if len(values) > 0 else 'Col1':<40} {headers[1] if len(headers) > 1 else 'Col2':<40}")
                    print("-" * 130)
                    
                    for idx, row in enumerate(values[1:21], 1):
                        if row:
                            col1 = (row[0] if len(row) > 0 else "")[:40]
                            col2 = (row[1] if len(row) > 1 else "")[:40]
                            try:
                                print(f"{idx:<5} {col1:<40} {col2:<40}")
                            except:
                                print(f"{idx:<5} [Non-ASCII content]")

                    if len(values) > 21:
                        print(f"\n... and {len(values) - 21} more rows")

            except Exception as e:
                print(f"Error reading {title}: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
