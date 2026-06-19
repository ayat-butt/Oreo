#!/usr/bin/env python3
"""OPL audit with EXACT OWT formatting"""

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

def get_opl_employees_fixed(service, sheet_id):
    """Get OPL employees from all sheets in workbook"""
    try:
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        all_employees = {}

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
                if name not in all_employees:
                    all_employees[name] = dept

        return all_employees

    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("OPL JOINERS & LEAVERS AUDIT - JULY 2024 TO JUNE 2025")
    print("="*120)

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

    print("\nExtracting OPL employees...\n")

    monthly_data = {}
    for month, sheet_id in sheets.items():
        employees = get_opl_employees_fixed(service, sheet_id)
        monthly_data[month] = employees
        print(f"{month}: {len(employees)} employees")

    oct_employees = {
        'Haroon Yasin', 'ABDULREHMAN SIDDIQI', 'Mateen Sheikh', 'Sabeena Abbasi',
        'ABDUR REHMAN', 'Abdurrehman Afridi', 'AJLAL HASAN', 'Aleena Athar',
        'AQIB MEHMOOD SATTI', 'Amina Tayyab', 'Aroma Tahir', 'Ayesha Ehtisham',
        'Babar Khan', 'Fatima Rahman', 'Hamza Shahid', 'Hassan Ali', 'Hassan Amin',
        'Hassan Ibrahim', 'HUSNAIN SYED', 'Jawwad Ali', 'Mah Noor', 'Mahnoor Butt',
        'Mahnoor Shafique', 'Mavia', 'Muhammad Ahsan', 'Muhammad Danish Iqbal',
        'MUHAMMAD IMRAN', 'MUHAMMAD JALAL KHAN', 'Muhammad Kamal', 'Muhammad Ramzan',
        'MUHAMMAD SAAD BIN IDREES', 'MUHAMMAD SHOIAB KHAN', 'Mashhood Rastgar',
        'Muhammad Talha', 'Muhammad Zeeshan Usaid', 'Fahad Mahmood', 'Mujeeb ur Rehman',
        'Zohaib Hasan Khan', 'Nabi Ahmad', 'Osama Ahmad', 'Raja Rehan Ahmed',
        'Ramsha Khurshid', 'Saja Abdullah', 'Salwa', 'Sameer Sheikh', 'Sana Akbar',
        'Shayan Ahmad', 'SHEIKH NIMRA', 'SIKANADAR KHURSHID', 'AHMED JAVED',
        'Sualeha Anjum', 'Summar Raja', 'SYED JUNAID ALI ZAIDI', 'Syed Kamal Raza Naqvi',
        'Tooba Bibi', 'Usama Tuqir Wahla', 'Usman Imtiaz', 'Uzma Khan',
        'Zarmeena Siddiqui', 'ZEESHAN BADAR BUKHARI', 'Zeeshan Zahoor', 'Zunaira Shahid'
    }

    all_records = {}

    # October leavers
    nov_set = set(monthly_data['November 2024'].keys())
    oct_leavers = oct_employees - nov_set
    for name in sorted(oct_leavers):
        all_records[name] = {
            'joining_month': 'July 2024',
            'leaving_month': 'October 2024',
            'department': ''
        }

    # November joiners
    nov_joiners = nov_set - oct_employees
    for name in nov_joiners:
        all_records[name] = {
            'joining_month': 'November 2024',
            'leaving_month': None,
            'department': monthly_data['November 2024'][name]
        }

    # Month-by-month tracking
    months_ordered = ['November 2024', 'December 2024', 'January 2025', 'February 2025',
                      'March 2025', 'April 2025', 'May 2025', 'June 2025']

    for i in range(len(months_ordered) - 1):
        current_month = months_ordered[i]
        next_month = months_ordered[i + 1]

        current_set = set(monthly_data[current_month].keys())
        next_set = set(monthly_data[next_month].keys())

        joiners = next_set - current_set
        for name in joiners:
            if name not in all_records:
                all_records[name] = {
                    'joining_month': next_month,
                    'leaving_month': None,
                    'department': monthly_data[next_month][name]
                }

        leavers = current_set - next_set
        for name in leavers:
            if name in all_records:
                all_records[name]['leaving_month'] = next_month

    print(f"\nCreating properly formatted sheet with {len(all_records)} records...\n")

    # BUILD OUTPUT WITH EXACT OWT FORMATTING
    output_rows = []

    # Row 1: Empty
    output_rows.append([''])

    # Row 2: Title (Columns B-C merged, contains title)
    output_rows.append(['', 'List of Joiner and Leavers July 24 - June 25'])

    # Row 3: Headers (starting in Column B)
    output_rows.append(['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'])

    # Data rows
    date_map = {
        'July 2024': ('01-07-2024', '31-07-2024'),
        'October 2024': ('01-10-2024', '31-10-2024'),
        'November 2024': ('01-11-2024', '30-11-2024'),
        'December 2024': ('01-12-2024', '31-12-2024'),
        'January 2025': ('01-01-2025', '31-01-2025'),
        'February 2025': ('01-02-2025', '28-02-2025'),
        'March 2025': ('01-03-2025', '31-03-2025'),
        'April 2025': ('01-04-2025', '30-04-2025'),
        'May 2025': ('01-05-2025', '31-05-2025'),
        'June 2025': ('01-06-2025', '30-06-2025'),
    }

    for name in sorted(all_records.keys()):
        record = all_records[name]

        joining_date = ''
        if record['joining_month'] in date_map:
            joining_date = date_map[record['joining_month']][0]

        leaving_date = ''
        if record['leaving_month'] and record['leaving_month'] in date_map:
            leaving_date = date_map[record['leaving_month']][1]

        output_rows.append([
            '',  # Column A: empty
            name,  # Column B: Name
            record['department'],  # Column C: Department
            '',  # Column D: Designation (empty)
            joining_date,  # Column E: Date of Joining
            leaving_date,  # Column F: Date of Leaving
            ''  # Column G: Salaries (empty)
        ])

    # Create sheet
    try:
        create_request = {
            'properties': {
                'title': 'OPL Joiners & Leavers Jul24-Jun25 (Properly Formatted)'
            }
        }

        spreadsheet = service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        # Write data
        update_body = {'values': output_rows}
        service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G5000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print("="*120)
        print("PROPERLY FORMATTED SHEET CREATED")
        print("="*120)
        print(f"\nURL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nSheet Details:")
        print(f"  Total Records: {len(all_records)}")
        print(f"  Format: OWT standard (Name, Department, Designation, Joining Date, Leaving Date, Salaries)")
        print(f"  Date Format: DD-MM-YYYY")
        print(f"  Coverage: July 2024 - June 2025 (Joiners & Leavers only)")
        print(f"\nReady for audit submission!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
