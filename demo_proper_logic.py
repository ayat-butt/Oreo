#!/usr/bin/env python3
"""
Demonstrates the CORRECT cross-checking logic for Nov 2024 - June 2025
Once you provide July-October data, this same logic will apply to the full period
"""

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

def get_opl_from_sheets(service, sheet_id):
    """Extract OPL employees from Google Sheets"""
    employees = {}

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
            if not rows:
                continue

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

            for row_idx in range(header_row + 1, len(rows)):
                row = rows[row_idx]
                if not row or len(row) <= name_col:
                    continue

                name = str(row[name_col]).strip() if name_col < len(row) else ''
                if not name or 'total' in name.lower() or len(name) < 3:
                    continue

                dept = str(row[dept_col]).strip() if dept_col and dept_col < len(row) else ''
                if name not in employees:
                    employees[name] = {'department': dept}

    except Exception as e:
        print(f"  Error: {e}")

    return employees

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    sheets_service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("DEMONSTRATION: PROPER MONTH-BY-MONTH CROSS-CHECKING LOGIC")
    print("="*120)
    print("\nThis demonstrates the CORRECT logic:")
    print("- Compare Month X with Month X+1")
    print("- Leavers: In Month X but NOT in Month X+1")
    print("- Joiners: In Month X+1 but NOT in Month X")
    print("- Exclude: Present in BOTH months (continuously employed)")
    print("\n" + "="*120 + "\n")

    sheets = {
        'November 2024': '1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA',
        'December 2024': '1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E',
        'January 2025': '1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA',
        'February 2025': '1T5rMIo0Apv41Tm-jDstU1qT5Lp6raFGhBNaYPIR4oe0',
        'March 2025': '17qI-qwttshi_qWok5Xqbu5p2xDNt8SmvKx_g-QL-QPc',
        'April 2025': '1lOSgTwzvI0NudWB6voUXJaNhViAqBbCPhCURqTZQx8k',
        'May 2025': '1uhAxR4UCrY5OOmQHgfdpqOS_M3QeIUBt66YtojpRHD0',
        'June 2025': '1KtM9hkNIFEnvYWO8DFZf1iVSZungdiWdIGAsQTmu-Us',
    }

    # READ ALL MONTHS
    print("Reading OPL data from all months:\n")
    monthly_data = {}
    for month, sheet_id in sheets.items():
        employees = get_opl_from_sheets(sheets_service, sheet_id)
        monthly_data[month] = employees
        print(f"  {month}: {len(employees)} OPL employees")

    # CROSS-CHECKING LOGIC
    print("\n" + "="*120)
    print("CROSS-CHECKING RESULTS")
    print("="*120)

    joiner_leaver_records = {}
    months_ordered = list(monthly_data.keys())

    for i in range(len(months_ordered) - 1):
        current_month = months_ordered[i]
        next_month = months_ordered[i + 1]

        current_employees = set(monthly_data[current_month].keys())
        next_employees = set(monthly_data[next_month].keys())

        # LEAVERS: Present in current month but NOT in next month
        leavers = current_employees - next_employees
        print(f"\n{current_month} -> {next_month}:")
        print(f"  [LEAVERS] {len(leavers)} employees in {current_month} but NOT in {next_month}")

        for name in sorted(leavers):
            if name not in joiner_leaver_records:
                joiner_leaver_records[name] = {
                    'joining_month': 'Earlier',
                    'leaving_month': next_month,
                    'department': monthly_data[current_month][name].get('department', ''),
                }
            else:
                # Already marked as joiner, now marking leaving date
                joiner_leaver_records[name]['leaving_month'] = next_month

        # JOINERS: Present in next month but NOT in current month
        joiners = next_employees - current_employees
        print(f"  [JOINERS] {len(joiners)} employees in {next_month} but NOT in {current_month}")

        for name in sorted(joiners):
            if name not in joiner_leaver_records:
                joiner_leaver_records[name] = {
                    'joining_month': next_month,
                    'leaving_month': None,
                    'department': monthly_data[next_month][name].get('department', ''),
                }

        # CONTINUOUSLY EMPLOYED (in both)
        continuous = current_employees & next_employees
        print(f"  [EXCLUDED] {len(continuous)} continuously employed (present in both months)")

    print(f"\n" + "="*120)
    print(f"TOTAL UNIQUE JOINERS & LEAVERS: {len(joiner_leaver_records)}")
    print(f"Period: November 2024 - June 2025")
    print("="*120)

    # CREATE OUTPUT SHEET
    print(f"\nCreating output sheet with {len(joiner_leaver_records)} records...\n")

    output_rows = []
    output_rows.append([''])
    output_rows.append(['', 'List of Joiner and Leavers July 24 - June 25'])
    output_rows.append(['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'])

    date_map = {
        'November 2024': ('01-11-2024', '30-11-2024'),
        'December 2024': ('01-12-2024', '31-12-2024'),
        'January 2025': ('01-01-2025', '31-01-2025'),
        'February 2025': ('01-02-2025', '28-02-2025'),
        'March 2025': ('01-03-2025', '31-03-2025'),
        'April 2025': ('01-04-2025', '30-04-2025'),
        'May 2025': ('01-05-2025', '31-05-2025'),
        'June 2025': ('01-06-2025', '30-06-2025'),
    }

    for name in sorted(joiner_leaver_records.keys()):
        record = joiner_leaver_records[name]

        joining_date = ''
        if record['joining_month'] in date_map:
            joining_date = date_map[record['joining_month']][0]

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

    # Create Google Sheet
    try:
        create_request = {
            'properties': {
                'title': 'OPL Joiners-Leavers Nov24-Jun25 (Properly Cross-Checked)'
            }
        }

        spreadsheet = sheets_service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        update_body = {'values': output_rows}
        sheets_service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G5000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print("="*120)
        print("SHEET CREATED WITH PROPER CROSS-CHECKING LOGIC")
        print("="*120)
        print(f"\nURL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nNote: This covers November 2024 - June 2025")
        print(f"To include July-October 2024, please provide the employee lists or access to those sheets")

    except Exception as e:
        print(f"Error creating sheet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
