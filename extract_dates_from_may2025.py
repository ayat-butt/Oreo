#!/usr/bin/env python3
"""Extract joining/leaving dates from May 2025 addition/deletion records"""

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

# Audit sheet - check all monthly tabs for OPL data
spreadsheet_id = '1-GEd1hIU7OOJ-CP97VqnrW1p0TPTXhzDAlgim08HLJM'

try:
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get('sheets', [])

    all_joining_dates = {}
    all_leaving_dates = {}

    # Check all sheets
    for sheet in sheets:
        title = sheet['properties']['title']

        # Fetch data
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{title}'!A1:I200"
            ).execute()

            rows = result.get('values', [])

            # Look for EMPLOYEE ADDITION section
            for i, row in enumerate(rows):
                if row and 'EMPLOYEE' in str(row[0]).upper() and 'ADDITION' in str(row[0]).upper():
                    # Found addition section
                    header_row = i + 1
                    if header_row < len(rows):
                        headers = rows[header_row]

                        name_col = None
                        entity_col = None
                        date_col = None

                        for col_idx, header in enumerate(headers):
                            h = str(header).lower()
                            if 'name' in h:
                                name_col = col_idx
                            elif 'opl' in h or 'owt' in h:
                                entity_col = col_idx
                            elif 'join' in h and 'date' in h:
                                date_col = col_idx

                        # Extract data
                        for row_idx in range(header_row + 1, min(header_row + 100, len(rows))):
                            row = rows[row_idx]
                            if not row or len(row) < 2 or not row[0].strip():
                                continue

                            name = row[name_col].strip() if name_col and name_col < len(row) else ''
                            entity = row[entity_col].strip() if entity_col and entity_col < len(row) else ''
                            join_date = row[date_col].strip() if date_col and date_col < len(row) else ''

                            if name and entity and 'OPL' in entity.upper() and join_date:
                                all_joining_dates[name] = join_date
                                print(f"[{title}] JOINER: {name} - Joined: {join_date}")

                # Look for EMPLOYEE SEPARATION section
                elif row and 'EMPLOYEE' in str(row[0]).upper() and 'SEPARAT' in str(row[0]).upper():
                    # Found separation section
                    header_row = i + 1
                    if header_row < len(rows):
                        headers = rows[header_row]

                        name_col = None
                        entity_col = None
                        date_col = None

                        for col_idx, header in enumerate(headers):
                            h = str(header).lower()
                            if 'name' in h:
                                name_col = col_idx
                            elif 'opl' in h or 'owt' in h:
                                entity_col = col_idx
                            elif 'separat' in h and 'date' in h:
                                date_col = col_idx

                        # Extract data
                        for row_idx in range(header_row + 1, min(header_row + 100, len(rows))):
                            row = rows[row_idx]
                            if not row or len(row) < 2 or not row[0].strip():
                                continue

                            name = row[name_col].strip() if name_col and name_col < len(row) else ''
                            entity = row[entity_col].strip() if entity_col and entity_col < len(row) else ''
                            sep_date = row[date_col].strip() if date_col and date_col < len(row) else ''

                            if name and entity and 'OPL' in entity.upper() and sep_date:
                                all_leaving_dates[name] = sep_date
                                print(f"[{title}] LEAVER: {name} - Left: {sep_date}")

        except:
            continue

    print(f"\n\nSummary:")
    print(f"  Total OPL joiners found: {len(all_joining_dates)}")
    print(f"  Total OPL leavers found: {len(all_leaving_dates)}")

    # Save to file
    with open('output/OPL_EXTRACTED_DATES.txt', 'w') as f:
        f.write("OPL JOINING DATES\n")
        f.write("="*80 + "\n")
        for name, date in sorted(all_joining_dates.items()):
            f.write(f"{name}: {date}\n")

        f.write(f"\n\nOPL LEAVING DATES\n")
        f.write("="*80 + "\n")
        for name, date in sorted(all_leaving_dates.items()):
            f.write(f"{name}: {date}\n")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
