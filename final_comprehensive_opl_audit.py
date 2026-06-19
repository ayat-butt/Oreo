#!/usr/bin/env python3
"""Final comprehensive OPL audit with all sheet data"""

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

def get_employees(service, sheet_id, sheet_name):
    """Extract employees from sheet"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{sheet_name}'!A1:Z500"
        ).execute()

        rows = result.get('values', [])

        # Find header with employee column
        header_row = None
        for i, row in enumerate(rows[:15]):
            if row and any('employee' in str(cell).lower() for cell in row):
                header_row = i
                break

        if header_row is None:
            return {}

        headers = rows[header_row]
        name_col = None
        dept_col = None

        for col_idx, header in enumerate(headers):
            h = str(header).lower()
            if 'employee' in h and 'name' in h:
                name_col = col_idx
            elif 'depart' in h and dept_col is None:
                dept_col = col_idx

        if name_col is None:
            return {}

        employees = {}
        for row_idx in range(header_row + 1, len(rows)):
            row = rows[row_idx]
            if not row or len(row) < 2:
                continue

            name = row[name_col].strip() if name_col and name_col < len(row) else ''
            if not name or 'total' in name.lower() or len(name) < 3:
                continue

            # Filter out obvious non-employee entries
            if any(word in name.upper() for word in ['BANK', 'LIMITED', 'LTD', 'FAYSAL', 'MOBILINK', 'ASKARI']):
                continue

            dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
            employees[name] = {'department': dept}

        return employees

    except Exception as e:
        return {}

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    service = build('sheets', 'v4', credentials=creds)

    # Map sheets to months
    sheets_map = [
        ('1jBlbB-Ff54udES4o_G_-qhB8aAuW53Hb1jRlGNDmZ3E', 'August 2024'),
        ('1IklN-MJqHjKlXI6s1B3I58_JGnOi0I0tEoO0rf3wkwY', 'September 2024'),
        ('1Fi_BVfQAwDi5tSPhvRWK6dPSgCOPVYoBOhNQ81zcTBI', 'October 2024'),
        ('1wdTogupsdtkcOEXgQWNwsiJNnUOwx-87JYcpv6MSop4', 'November 2024'),
        ('1_A5o1Aln9AjEmjX-BzXyWfHdzLajYvwiRVmRtiKH4hs', 'December 2024'),
        ('14rfFm49DNyESepj5Lfux1OG1QYbv5QtDTUXYh1FuNUU', 'January 2025'),
        ('1e83npqk4HQmm0_ELlbdqJFZDXwbkz94V4RGUjpdOzE0', 'February 2025'),
        ('1ahND0ab4mIOe1_dduUt-2tuxKvdugoEyNd2qh8HV5TQ', 'March 2025'),
        ('1cENuT5O49O5f-ut621XlJqQ0yWFni0x6G8TNAzK6hzU', 'April 2025'),
        ('1drSWY44h-INF3aE6TIvrqT-MFuXc1DTLoWrFMBXxUNU', 'May 2025'),
        ('1C6sZRGVqvLrt5kKMx7jwIw7EoI4tbgHeqpmohScPXIo', 'June 2025'),
    ]

    print("="*120)
    print("FINAL COMPREHENSIVE OPL AUDIT: AUGUST 2024 - JUNE 2025")
    print("="*120)
    print("\nExtracting data from each month...\n")

    monthly_data = {}
    for sheet_id, month in sheets_map:
        print(f"Processing {month}...", end=' ')

        # Get sheet metadata to find OPL tab
        try:
            metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            sheets = metadata.get('sheets', [])

            opl_sheet = None
            for sheet in sheets:
                title = sheet['properties']['title']
                if 'OPL' in title.upper():
                    opl_sheet = title
                    break

            if not opl_sheet:
                opl_sheet = sheets[0]['properties']['title'] if sheets else 'OPL'

            employees = get_employees(service, sheet_id, opl_sheet)
            monthly_data[month] = employees

            print(f"Found {len(employees)} employees")
        except Exception as e:
            print(f"Error: {e}")
            monthly_data[month] = {}

    # Analyze month-to-month changes
    print("\n" + "="*120)
    print("MONTH-BY-MONTH ANALYSIS")
    print("="*120)

    months_ordered = ['August 2024', 'September 2024', 'October 2024', 'November 2024',
                      'December 2024', 'January 2025', 'February 2025', 'March 2025',
                      'April 2025', 'May 2025', 'June 2025']

    all_joiners = {}
    all_leavers = {}

    print(f"\nAugust 2024 (Opening): {len(monthly_data['August 2024'])} employees")

    for i in range(len(months_ordered) - 1):
        current_month = months_ordered[i]
        next_month = months_ordered[i + 1]

        current_set = set(monthly_data[current_month].keys())
        next_set = set(monthly_data[next_month].keys())

        joiners = next_set - current_set
        leavers = current_set - next_set

        if joiners:
            print(f"\n[JOINERS] {current_month} -> {next_month}: {len(joiners)} new employees")
            for name in sorted(joiners):
                if name not in all_joiners:
                    all_joiners[name] = next_month

        if leavers:
            print(f"[LEAVERS] {current_month} -> {next_month}: {len(leavers)} employees left")
            for name in sorted(leavers):
                if name not in all_leavers:
                    all_leavers[name] = next_month

    # Create final sheet data
    print("\n" + "="*120)
    print("BUILDING FINAL SHEET")
    print("="*120)

    output_rows = [
        [''],
        ['', 'List of Joiner and Leavers July 24 - June 25'],
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'],
    ]

    # Add all records
    all_names = set()
    for month_data in monthly_data.values():
        all_names.update(month_data.keys())

    for name in sorted(all_names):
        joining_month = None
        leaving_month = None
        dept = ''

        # Find joining month
        for month in months_ordered:
            if name in monthly_data[month]:
                if joining_month is None:
                    joining_month = month
                    dept = monthly_data[month][name].get('department', '')
                leaving_month = month

        # Determine dates
        joining_date = ''
        leaving_date = ''

        if joining_month:
            # Format joining date
            if 'August' in joining_month:
                joining_date = '1st August 2024'
            elif 'September' in joining_month:
                joining_date = '1st September 2024'
            elif 'October' in joining_month:
                joining_date = '1st October 2024'
            elif 'November' in joining_month:
                joining_date = '1st November 2024'
            elif 'December' in joining_month:
                joining_date = '1st December 2024'
            elif 'January' in joining_month:
                joining_date = '1st January 2025'
            elif 'February' in joining_month:
                joining_date = '1st February 2025'
            elif 'March' in joining_month:
                joining_date = '1st March 2025'
            elif 'April' in joining_month:
                joining_date = '1st April 2025'
            elif 'May' in joining_month:
                joining_date = '1st May 2025'

        if leaving_month and leaving_month != months_ordered[-1]:
            # Determine next month
            idx = months_ordered.index(leaving_month)
            if idx < len(months_ordered) - 1:
                next_month_name = months_ordered[idx + 1]
                # Format leaving date as last day of leaving_month
                if 'August' in leaving_month:
                    leaving_date = '31st August 2024'
                elif 'September' in leaving_month:
                    leaving_date = '30th September 2024'
                elif 'October' in leaving_month:
                    leaving_date = '31st October 2024'
                elif 'November' in leaving_month:
                    leaving_date = '30th November 2024'
                elif 'December' in leaving_month:
                    leaving_date = '31st December 2024'
                elif 'January' in leaving_month:
                    leaving_date = '31st January 2025'
                elif 'February' in leaving_month:
                    leaving_date = '28th February 2025'
                elif 'March' in leaving_month:
                    leaving_date = '31st March 2025'
                elif 'April' in leaving_month:
                    leaving_date = '30th April 2025'
                elif 'May' in leaving_month:
                    leaving_date = '31st May 2025'

        output_rows.append([
            '',
            name,
            dept,
            '',
            joining_date,
            leaving_date,
            ''
        ])

    # Create sheet
    print(f"\nCreating Google Sheet with {len(all_names)} employees...")

    try:
        create_request = {
            'properties': {
                'title': 'OPL List of Joiners and Leavers 2024-2025 (Final Complete)'
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

        print(f"\n{'='*120}")
        print(f"FINAL OPL SHEET CREATED!")
        print(f"{'='*120}")
        print(f"\nURL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nData Summary:")
        print(f"  Total employees tracked: {len(all_names)}")
        print(f"  Total new joiners: {len(all_joiners)}")
        print(f"  Total employees who left: {len(all_leavers)}")

        # Save summary
        with open('output/FINAL_OPL_AUDIT_SUMMARY.txt', 'w') as f:
            f.write("FINAL OPL COMPREHENSIVE AUDIT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total employees: {len(all_names)}\n")
            f.write(f"New joiners: {len(all_joiners)}\n")
            f.write(f"Leavers: {len(all_leavers)}\n\n")
            f.write(f"Sheet URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}\n")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
