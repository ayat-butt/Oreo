#!/usr/bin/env python3
"""Create comprehensive OPL Joiners & Leavers sheet with complete data"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import requests
import pandas as pd
from io import BytesIO

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

def read_excel_from_drive(sheet_id):
    """Read Excel file from Google Drive"""
    try:
        download_url = f"https://docs.google.com/spreadsheets/export?id={sheet_id}&exportFormat=xlsx"
        response = requests.get(download_url, timeout=30)
        if response.status_code == 200:
            excel_file = BytesIO(response.content)
            xls = pd.ExcelFile(excel_file)
            df = pd.read_excel(excel_file, sheet_name=xls.sheet_names[0])
            return df
        return None
    except:
        return None

def extract_employees_from_df(df):
    """Extract employees from dataframe"""
    employees = {}
    name_col = None
    dept_col = None

    for col in df.columns:
        col_lower = str(col).lower().strip()
        if 'employee' in col_lower and 'name' in col_lower:
            name_col = col
        elif 'depart' in col_lower and dept_col is None:
            dept_col = col

    if name_col is None:
        return employees

    for idx, row in df.iterrows():
        name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
        if not name or name.lower() == 'nan' or len(name) < 3:
            continue

        dept = str(row[dept_col]).strip() if dept_col and pd.notna(row[dept_col]) else ""
        employees[name] = {'department': dept}

    return employees

def get_sheet_employees(service, sheet_id, sheet_name):
    """Get employees from Google Sheet"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{sheet_name}'!A1:Z500"
        ).execute()

        rows = result.get('values', [])
        header_row = None
        for i, row in enumerate(rows[:10]):
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
            if 'employee' in h and name_col is None:
                name_col = col_idx
            elif 'depart' in h:
                dept_col = col_idx

        employees = {}
        for row_idx in range(header_row + 1, len(rows)):
            row = rows[row_idx]
            if not row or len(row) < 2:
                continue

            name = row[name_col].strip() if name_col and name_col < len(row) else ''
            if not name or 'total' in name.lower() or len(name) < 3:
                continue

            dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
            employees[name] = {'department': dept}

        return employees
    except:
        return {}

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("EXTRACTING DATA FROM ALL MONTHS")
    print("="*120)

    # Get July 2024
    print("\n1. Reading July 2024 (Excel file)...")
    july_df = read_excel_from_drive('1tIKIU0LKCR2YYuCS0u0lb_Gr-rDm6ks_')
    july_employees = extract_employees_from_df(july_df) if july_df is not None else {}
    print(f"   Found {len(july_employees)} employees")

    # Get November 2024
    print("2. Reading November 2024...")
    nov_employees = get_sheet_employees(service, '1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA', 'OPL')
    print(f"   Found {len(nov_employees)} employees")

    # Get December 2024
    print("3. Reading December 2024...")
    dec_employees = get_sheet_employees(service, '1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E', 'OPL')
    print(f"   Found {len(dec_employees)} employees")

    # Get January 2025
    print("4. Reading January 2025...")
    jan_employees = get_sheet_employees(service, '1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA', 'OPL')
    print(f"   Found {len(jan_employees)} employees")

    # Get May 2025
    print("5. Reading May 2025...")
    may_employees = get_sheet_employees(service, '1uhAxR4UCrY5OOmQHgfdpqOS_M3QeIUBt66YtojpRHD0', 'OPL')
    print(f"   Found {len(may_employees)} employees")

    # Get June 2025
    print("6. Reading June 2025...")
    june_employees = get_sheet_employees(service, '1KtM9hkNIFEnvYWO8DFZf1iVSZungdiWdIGAsQTmu-Us', 'OPL')
    print(f"   Found {len(june_employees)} employees")

    print("\n" + "="*120)
    print("ANALYSIS: IDENTIFYING ALL JOINERS AND LEAVERS")
    print("="*120)

    # Identify leavers (July to November)
    july_set = set(july_employees.keys())
    nov_set = set(nov_employees.keys())
    july_leavers = july_set - nov_set
    july_continuing = july_set & nov_set

    print(f"\nJuly 2024 to November 2024:")
    print(f"  Opening balance: {len(july_employees)}")
    print(f"  Continuing: {len(july_continuing)}")
    print(f"  Left (July-October): {len(july_leavers)}")
    print(f"  New joiners in November: {len(nov_set - july_set)}")

    # Identify leavers between subsequent months
    dec_set = set(dec_employees.keys())
    jan_set = set(jan_employees.keys())
    may_set = set(may_employees.keys())
    june_set = set(june_employees.keys())

    print(f"\nNovember to December: {len(nov_set - dec_set)} left")
    print(f"December to January: {len(dec_set - jan_set)} left, {len(jan_set - dec_set)} new joiners")
    print(f"January to May: {len(jan_set)} to {len(may_set)}")
    print(f"May to June: {len(may_set)} left")

    # Create comprehensive data for sheet
    all_records = []

    # Opening employees (July 2024)
    for name in sorted(july_employees.keys()):
        if name not in july_leavers:
            all_records.append({
                'name': name,
                'dept': july_employees[name].get('department', ''),
                'joining_date': '1st July 2024',
                'leaving_date': ''
            })

    # July leavers
    for name in sorted(july_leavers):
        all_records.append({
            'name': name,
            'dept': july_employees[name].get('department', ''),
            'joining_date': '1st July 2024',
            'leaving_date': '31st October 2024'
        })

    # November new joiners
    for name in sorted(nov_set - july_set):
        all_records.append({
            'name': name,
            'dept': nov_employees[name].get('department', ''),
            'joining_date': '1st November 2024',
            'leaving_date': '31st January 2025' if name in (dec_set - jan_set) else ''
        })

    # January new joiners
    for name in sorted(jan_set - dec_set):
        all_records.append({
            'name': name,
            'dept': jan_employees[name].get('department', ''),
            'joining_date': '1st January 2025',
            'leaving_date': '31st January 2025' if name not in may_set else ''
        })

    # May new joiners
    for name in sorted(may_set - jan_set):
        all_records.append({
            'name': name,
            'dept': may_employees[name].get('department', ''),
            'joining_date': '1st May 2025',
            'leaving_date': '31st May 2025'
        })

    # Build sheet rows
    output_rows = [
        [''],
        ['', 'List of Joiner and Leavers July 24 - June 25'],
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'],
    ]

    for record in all_records:
        output_rows.append([
            '',
            record['name'],
            record['dept'],
            '',
            record['joining_date'],
            record['leaving_date'],
            ''
        ])

    # Create sheet
    print(f"\n\nCreating Google Sheet with {len(all_records)} employees...")
    try:
        create_request = {
            'properties': {
                'title': 'OPL List of Joiners and Leavers 2024-2025 (Complete)'
            }
        }

        spreadsheet = service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        update_body = {'values': output_rows}
        service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G2000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print(f"\n{'='*120}")
        print(f"COMPREHENSIVE OPL SHEET CREATED!")
        print(f"{'='*120}")
        print(f"URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nData Summary:")
        print(f"  Total employees: {len(all_records)}")
        print(f"  Opening balance (July 2024): {len(july_employees)}")
        print(f"  Leavers (July-October): {len(july_leavers)}")
        print(f"  New joiners (November): {len(nov_set - july_set)}")
        print(f"  New joiners (January): {len(jan_set - dec_set)}")
        print(f"  New joiners (May): {len(may_set - jan_set)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
