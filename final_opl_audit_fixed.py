#!/usr/bin/env python3
"""Fixed OPL audit - properly extracts from all months including Feb/Apr/Jun"""

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

            # Find header row
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

            # Extract employees
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
        print(f"Error extracting from sheet: {e}")
        return {}

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("FIXED OPL AUDIT: JULY 2024 - JUNE 2025")
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

    print("\nExtracting OPL employees from Nov 2024 onwards...\n")

    monthly_data = {}
    for month, sheet_id in sheets.items():
        employees = get_opl_employees_fixed(service, sheet_id)
        monthly_data[month] = employees
        print(f"{month}: {len(employees)} employees")

    # October 2024 employees (manually from PDF)
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

    print(f"\nKEY DATA POINTS:")
    print(f"  July 2024: 131 employees (opening balance)")
    print(f"  October 2024: {len(oct_employees)} employees (from PDF)")
    print(f"  November 2024: {len(monthly_data['November 2024'])} employees")

    # Identify joiners and leavers
    print("\n" + "="*120)
    print("ANALYZING JOINERS AND LEAVERS (Oct 2024 onwards)")
    print("="*120)

    all_records = {}

    # October leavers
    nov_set = set(monthly_data['November 2024'].keys())
    oct_leavers = oct_employees - nov_set
    print(f"\nLeavers (Oct -> Nov 2024): {len(oct_leavers)} employees")
    for name in sorted(oct_leavers):
        all_records[name] = {
            'joining_month': 'July 2024',
            'leaving_month': 'October 2024',
            'department': ''
        }

    # November joiners
    nov_joiners = nov_set - oct_employees
    print(f"New Joiners (Oct -> Nov 2024): {len(nov_joiners)} employees")
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

        # New joiners
        joiners = next_set - current_set
        for name in joiners:
            if name not in all_records:
                all_records[name] = {
                    'joining_month': next_month,
                    'leaving_month': None,
                    'department': monthly_data[next_month][name]
                }

        # Leavers
        leavers = current_set - next_set
        for name in leavers:
            if name in all_records:
                all_records[name]['leaving_month'] = next_month

    # Build output
    print(f"\n" + "="*120)
    print(f"CREATING FINAL SHEET: {len(all_records)} Joiners & Leavers")
    print("="*120 + "\n")

    output_rows = [
        [''],
        ['', 'List of Joiner and Leavers July 24 - June 25'],
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'],
    ]

    date_map = {
        'July 2024': ('1st July 2024', '31st July 2024'),
        'October 2024': ('1st October 2024', '31st October 2024'),
        'November 2024': ('1st November 2024', '30th November 2024'),
        'December 2024': ('1st December 2024', '31st December 2024'),
        'January 2025': ('1st January 2025', '31st January 2025'),
        'February 2025': ('1st February 2025', '28th February 2025'),
        'March 2025': ('1st March 2025', '31st March 2025'),
        'April 2025': ('1st April 2025', '30th April 2025'),
        'May 2025': ('1st May 2025', '31st May 2025'),
        'June 2025': ('1st June 2025', '30th June 2025'),
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
        create_request = {'properties': {'title': 'OPL Joiners & Leavers Jul24-Jun25 (Fixed)'}}
        spreadsheet = service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        update_body = {'values': output_rows}
        service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G5000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print("="*120)
        print("FIXED AUDIT SHEET CREATED!")
        print("="*120)
        print(f"\nURL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nFinal Summary:")
        print(f"  Total Joiners & Leavers: {len(all_records)}")
        print(f"  Format: Exact OWT format")
        print(f"\nMonthly Data:")
        for month in months_ordered:
            print(f"  {month}: {len(monthly_data[month])} employees")

    except Exception as e:
        print(f"Error creating sheet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
