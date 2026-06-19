#!/usr/bin/env python3
"""
Audit script to extract joiners and leavers for OPL entity
for the period July 2024 - June 2025
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from datetime import datetime

def load_credentials():
    """Load stored Google OAuth token."""
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def parse_date(date_str):
    """Parse date string in various formats."""
    if not date_str or date_str.strip() == '':
        return None

    formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def main():
    # Load credentials
    print("Loading credentials...")
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    # Build Sheets API client
    service = build('sheets', 'v4', credentials=creds)

    # Sheet details from URL
    spreadsheet_id = '1-GEd1hIU7OOJ-CP97VqnrW1p0TPTXhzDAlgim08HLJM'

    try:
        # Get metadata to understand sheet structure
        print("Fetching sheet metadata...")
        metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"\nFound {len(sheets)} tabs:")
        for sheet in sheets:
            print(f"  - {sheet['properties']['title']}")

        # Read the first sheet (or main data sheet)
        main_sheet = sheets[0]['properties']['title']
        print(f"\nReading data from: {main_sheet}")

        # Read all data
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{main_sheet}'!A1:Z1000"
        ).execute()

        rows = result.get('values', [])

        if not rows:
            print("No data found in sheet")
            return

        # Extract headers
        headers = rows[0]
        print(f"\nHeaders: {headers}")

        # Find column indices
        col_map = {}
        for i, header in enumerate(headers):
            col_map[header.lower()] = i

        print(f"\nColumn mapping: {col_map}")

        # Find relevant columns (common naming patterns)
        entity_col = None
        name_col = None
        joining_col = None
        leaving_col = None

        for key in col_map:
            if 'entity' in key or 'company' in key or 'organization' in key:
                entity_col = col_map[key]
            if 'name' in key or 'employee' in key:
                name_col = col_map[key]
            if 'join' in key or 'doj' in key:
                joining_col = col_map[key]
            if 'leav' in key or 'dol' in key or 'exit' in key:
                leaving_col = col_map[key]

        print(f"\nIdentified columns:")
        print(f"  Entity: {entity_col}")
        print(f"  Name: {name_col}")
        print(f"  Joining Date: {joining_col}")
        print(f"  Leaving Date: {leaving_col}")

        # Parse date range
        start_date = datetime(2024, 7, 1)
        end_date = datetime(2025, 6, 30)

        joiners = []
        leavers = []

        # Process data rows
        for row_idx in range(1, len(rows)):
            row = rows[row_idx]

            # Skip empty rows
            if not row or len(row) == 0:
                continue

            # Extract entity
            entity = row[entity_col].strip() if entity_col and entity_col < len(row) else None

            # Only process OPL
            if not entity or entity.upper() != 'OPL':
                continue

            name = row[name_col].strip() if name_col and name_col < len(row) else None
            joining_date_str = row[joining_col].strip() if joining_col and joining_col < len(row) else None
            leaving_date_str = row[leaving_col].strip() if leaving_col and leaving_col < len(row) else None

            joining_date = parse_date(joining_date_str) if joining_date_str else None
            leaving_date = parse_date(leaving_date_str) if leaving_date_str else None

            # Check if joiner
            if joining_date and start_date <= joining_date <= end_date:
                joiners.append({
                    'name': name,
                    'joining_date': joining_date_str,
                    'entity': entity
                })

            # Check if leaver
            if leaving_date and start_date <= leaving_date <= end_date:
                leavers.append({
                    'name': name,
                    'leaving_date': leaving_date_str,
                    'joining_date': joining_date_str,
                    'entity': entity
                })

        # Output results
        print("\n" + "="*80)
        print(f"AUDIT REPORT: OPL Joiners & Leavers (July 2024 - June 2025)")
        print("="*80)

        print(f"\n### JOINERS ({len(joiners)} total)")
        print("-" * 80)
        if joiners:
            for i, joiner in enumerate(joiners, 1):
                print(f"{i}. {joiner['name']} - Joined: {joiner['joining_date']}")
        else:
            print("No joiners found")

        print(f"\n### LEAVERS ({len(leavers)} total)")
        print("-" * 80)
        if leavers:
            for i, leaver in enumerate(leavers, 1):
                print(f"{i}. {leaver['name']} - Left: {leaver['leaving_date']} (Joined: {leaver['joining_date']})")
        else:
            print("No leavers found")

        print(f"\n### SUMMARY")
        print("-" * 80)
        print(f"Total Joiners: {len(joiners)}")
        print(f"Total Leavers: {len(leavers)}")
        print(f"Net Change: {len(joiners) - len(leavers)}")

        # Save to output file
        output_file = 'output/OPL_Audit_Report_Jul2024_Jun2025.txt'
        with open(output_file, 'w') as f:
            f.write(f"AUDIT REPORT: OPL Joiners & Leavers (July 2024 - June 2025)\n")
            f.write(f"{'='*80}\n\n")

            f.write(f"### JOINERS ({len(joiners)} total)\n")
            f.write(f"{'-'*80}\n")
            for i, joiner in enumerate(joiners, 1):
                f.write(f"{i}. {joiner['name']} - Joined: {joiner['joining_date']}\n")

            f.write(f"\n### LEAVERS ({len(leavers)} total)\n")
            f.write(f"{'-'*80}\n")
            for i, leaver in enumerate(leavers, 1):
                f.write(f"{i}. {leaver['name']} - Left: {leaver['leaving_date']} (Joined: {leaver['joining_date']})\n")

            f.write(f"\n### SUMMARY\n")
            f.write(f"{'-'*80}\n")
            f.write(f"Total Joiners: {len(joiners)}\n")
            f.write(f"Total Leavers: {len(leavers)}\n")
            f.write(f"Net Change: {len(joiners) - len(leavers)}\n")

        print(f"\nReport saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
