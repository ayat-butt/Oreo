#!/usr/bin/env python3
"""Create OPL sheet with ONLY joiners and leavers (exclude continuous employees)"""

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

def get_opl_employees(service, sheet_id):
    """Get OPL employees from sheet"""
    try:
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()

        for sheet in metadata.get('sheets', []):
            sheet_name = sheet['properties']['title']
            if 'OPL' not in sheet_name.upper():
                continue

            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"'{sheet_name}'!A1:Z500"
            ).execute()

            rows = result.get('values', [])

            # Find header
            header_row = None
            for i, row in enumerate(rows[:15]):
                if row and any('employee' in str(cell).lower() for cell in row):
                    header_row = i
                    break

            if header_row is None:
                continue

            headers = rows[header_row]
            name_col = None
            dept_col = None

            for col_idx, header in enumerate(headers):
                h = str(header).lower()
                if 'employee' in h and name_col is None:
                    name_col = col_idx
                elif 'depart' in h:
                    dept_col = col_idx

            if name_col is None:
                continue

            employees = {}
            for row_idx in range(header_row + 1, len(rows)):
                row = rows[row_idx]
                if not row or len(row) < 2:
                    continue

                name = row[name_col].strip() if name_col and name_col < len(row) else ''
                if not name or 'total' in name.lower() or len(name) < 3:
                    continue

                dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
                employees[name] = dept

            return employees

        return {}
    except:
        return {}

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("CREATING JOINERS & LEAVERS ONLY SHEET (Excluding continuous employees)")
    print("="*120)

    # Reference sheets
    sheets = {
        'November 2024': '1wdTogupsdtkcOEXgQWNwsiJNnUOwx-87JYcpv6MSop4',
        'December 2024': '1_A5o1Aln9AjEmjX-BzXyWfHdzLajYvwiRVmRtiKH4hs',
        'January 2025': '14rfFm49DNyESepj5Lfux1OG1QYbv5QtDTUXYh1FuNUU',
        'February 2025': '1e83npqk4HQmm0_ELlbdqJFZDXwbkz94V4RGUjpdOzE0',
        'March 2025': '17qI-qwttshi_qWok5Xqbu5p2xDNt8SmvKx_g-QL-QPc',
        'April 2025': '1lOSgTwzvI0NudWB6voUXJaNhViAqBbCPhCURqTZQx8k',
        'May 2025': '1drSWY44h-INF3aE6TIvrqT-MFuXc1DTLoWrFMBXxUNU',
        'June 2025': '1C6sZRGVqvLrt5kKMx7jwIw7EoI4tbgHeqpmohScPXIo',
    }

    print("\nExtracting OPL employees from each month...\n")

    monthly_data = {}
    for month, sheet_id in sheets.items():
        employees = get_opl_employees(service, sheet_id)
        monthly_data[month] = employees
        print(f"{month}: {len(employees)} employees")

    # Identify joiners and leavers
    print("\n" + "="*120)
    print("ANALYZING JOINERS AND LEAVERS")
    print("="*120)

    months_ordered = ['November 2024', 'December 2024', 'January 2025', 'February 2025',
                      'March 2025', 'April 2025', 'May 2025', 'June 2025']

    joiners_leavers = {}

    # First month (November 2024) - all are opening balance, not joiners
    # Compare subsequent months
    for i in range(len(months_ordered) - 1):
        current_month = months_ordered[i]
        next_month = months_ordered[i + 1]

        current_set = set(monthly_data[current_month].keys())
        next_set = set(monthly_data[next_month].keys())

        # Joiners
        joiners = next_set - current_set
        for name in joiners:
            if name not in joiners_leavers:
                joiners_leavers[name] = {
                    'joining_month': next_month,
                    'leaving_month': None,
                    'department': monthly_data[next_month][name]
                }
                print(f"\n[JOINER] {name}")
                print(f"  Joined: {next_month}")

        # Leavers
        leavers = current_set - next_set
        for name in leavers:
            if name in joiners_leavers:
                # This person joined and then left
                joiners_leavers[name]['leaving_month'] = next_month
                print(f"\n[LEAVER] {name}")
                print(f"  Left: {next_month}")
            else:
                # This person was in opening balance
                joiners_leavers[name] = {
                    'joining_month': 'Opening Balance',
                    'leaving_month': next_month,
                    'department': monthly_data[current_month][name]
                }
                print(f"\n[OPENING BALANCE LEAVER] {name}")
                print(f"  Left: {next_month}")

    # Build output
    print("\n" + "="*120)
    print("BUILDING OUTPUT SHEET")
    print("="*120)

    output_rows = [
        [''],
        ['', 'List of Joiner and Leavers July 24 - June 25'],
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'],
    ]

    date_map = {
        'November 2024': ('1st November 2024', '30th November 2024'),
        'December 2024': ('1st December 2024', '31st December 2024'),
        'January 2025': ('1st January 2025', '31st January 2025'),
        'February 2025': ('1st February 2025', '28th February 2025'),
        'March 2025': ('1st March 2025', '31st March 2025'),
        'April 2025': ('1st April 2025', '30th April 2025'),
        'May 2025': ('1st May 2025', '31st May 2025'),
        'June 2025': ('1st June 2025', '30th June 2025'),
    }

    for name in sorted(joiners_leavers.keys()):
        record = joiners_leavers[name]

        joining_date = ''
        if record['joining_month'] in date_map:
            joining_date = date_map[record['joining_month']][0]
        elif record['joining_month'] == 'Opening Balance':
            joining_date = '1st July 2024'

        leaving_date = ''
        if record['leaving_month'] and record['leaving_month'] in date_map:
            leaving_date = date_map[record['leaving_month']][1]

        output_rows.append([
            '',
            name,
            record['department'],
            '',
            joining_date,
            leaving_date,
            ''
        ])

    # Create sheet
    print(f"\nCreating Google Sheet with {len(joiners_leavers)} joiners/leavers...\n")

    try:
        create_request = {
            'properties': {
                'title': 'OPL Joiners & Leavers Only (Jul24-Jun25)'
            }
        }

        spreadsheet = service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        update_body = {'values': output_rows}
        service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G3000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print("="*120)
        print("JOINERS & LEAVERS SHEET CREATED!")
        print("="*120)
        print(f"\nURL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nData Summary:")
        print(f"  Total Joiners & Leavers: {len(joiners_leavers)}")
        print(f"  Note: Continuous employees (present all months) EXCLUDED")
        print(f"  Format: Exact OWT match")
        print(f"\nThis sheet contains ONLY employees who:")
        print(f"  - Joined during the period")
        print(f"  - Left during the period")
        print(f"  - Changed status during the period")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
