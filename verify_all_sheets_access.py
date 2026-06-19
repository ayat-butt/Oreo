#!/usr/bin/env python3
"""Verify access to ALL sheets from July 2024 to June 2025"""

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

def check_sheet_access(service, sheet_id, month_label):
    """Check if sheet is accessible and get employee count"""
    try:
        print(f"\n{month_label}:")
        print(f"  Sheet ID: {sheet_id}")

        # Try to get metadata
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"  Sheets found: {len(sheets)}")
        sheet_names = [s['properties']['title'] for s in sheets]
        print(f"  Sheet names: {sheet_names}")

        # Try to find OPL sheet
        opl_sheet = None
        for sheet in sheets:
            title = sheet['properties']['title']
            if 'OPL' in title.upper():
                opl_sheet = title
                break

        if not opl_sheet:
            opl_sheet = sheet_names[0] if sheet_names else None

        if not opl_sheet:
            print(f"  Status: ACCESSIBLE but no OPL sheet found")
            return {'accessible': True, 'has_opl': False, 'employee_count': 0}

        print(f"  Reading OPL sheet: '{opl_sheet}'")

        # Try to fetch data
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{opl_sheet}'!A1:Z500"
        ).execute()

        rows = result.get('values', [])
        print(f"  Data retrieved: {len(rows)} rows")

        # Find header
        header_row = None
        for i, row in enumerate(rows[:15]):
            if row and any('employee' in str(cell).lower() for cell in row):
                header_row = i
                break

        if header_row is None:
            print(f"  Status: ACCESSIBLE but no employee data found")
            return {'accessible': True, 'has_opl': True, 'employee_count': 0}

        # Count employees
        employee_count = 0
        for row_idx in range(header_row + 1, len(rows)):
            row = rows[row_idx]
            if row and len(row) > 0:
                employee_count += 1

        print(f"  Status: ACCESSIBLE - {employee_count} employee rows found")
        return {'accessible': True, 'has_opl': True, 'employee_count': employee_count}

    except Exception as e:
        error_msg = str(e)
        if '401' in error_msg or 'Unauthorized' in error_msg:
            print(f"  Status: PERMISSION DENIED (401)")
            return {'accessible': False, 'error': 'permission_denied'}
        elif '404' in error_msg or 'not found' in error_msg:
            print(f"  Status: NOT FOUND (404)")
            return {'accessible': False, 'error': 'not_found'}
        else:
            print(f"  Status: ERROR - {error_msg[:100]}")
            return {'accessible': False, 'error': str(e)[:100]}

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("VERIFICATION: ALL SHEETS FROM JULY 2024 TO JUNE 2025")
    print("="*120)

    # All sheets in order
    all_sheets = {
        'July 2024': '1tIKIU0LKCR2YYuCS0u0lb_Gr-rDm6ks_',
        'August 2024': '15n2DllSdSDErWwl0pj3PkeqwJKF5LDbZ',
        'September 2024': '1bP1Ju0vzcS7QxF1NkheVZpI6HxliE-F7',
        'October 2024': '1h1IRXwxx-mRAp0m2C2sqHlIjR5OzYpjc',
        'November 2024': '1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA',
        'December 2024': '1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E',
        'January 2025': '1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA',
        'February 2025': '1T5rMIo0Apv41Tm-jDstU1qT5Lp6raFGhBNaYPIR4oe0',
        'March 2025': '17qI-qwttshi_qWok5Xqbu5p2xDNt8SmvKx_g-QL-QPc',
        'April 2025': '1lOSgTwzvI0NudWB6voUXJaNhViAqBbCPhCURqTZQx8k',
        'May 2025': '1uhAxR4UCrY5OOmQHgfdpqOS_M3QeIUBt66YtojpRHD0',
        'June 2025': '1KtM9hkNIFEnvYWO8DFZf1iVSZungdiWdIGAsQTmu-Us',
    }

    results = {}
    for month, sheet_id in all_sheets.items():
        results[month] = check_sheet_access(service, sheet_id, month)

    # Summary
    print("\n" + "="*120)
    print("SUMMARY")
    print("="*120)

    accessible = {}
    not_accessible = {}
    no_data = {}

    for month, status in results.items():
        if status['accessible']:
            if status['has_opl']:
                if status['employee_count'] > 0:
                    accessible[month] = status['employee_count']
                else:
                    no_data[month] = 'No employee records'
            else:
                no_data[month] = 'No OPL sheet found'
        else:
            not_accessible[month] = status.get('error', 'Unknown error')

    print(f"\n✓ ACCESSIBLE & HAS DATA: {len(accessible)} months")
    for month, count in sorted(accessible.items()):
        print(f"  {month:<20} - {count} employees")

    print(f"\n⚠ ACCESSIBLE BUT NO/EMPTY DATA: {len(no_data)} months")
    for month, reason in sorted(no_data.items()):
        print(f"  {month:<20} - {reason}")

    print(f"\n✗ NOT ACCESSIBLE: {len(not_accessible)} months")
    for month, error in sorted(not_accessible.items()):
        print(f"  {month:<20} - {error}")

    print("\n" + "="*120)
    print("TOTAL COVERAGE:")
    print(f"  Total months: 12 (July 2024 - June 2025)")
    print(f"  Accessible with data: {len(accessible)}")
    print(f"  Accessible but no data: {len(no_data)}")
    print(f"  Not accessible: {len(not_accessible)}")
    print(f"  Coverage: {len(accessible)}/12 months ({int(len(accessible)*100/12)}%)")
    print("="*120)

    if not_accessible:
        print("\nSHEETS THAT COULD NOT BE ACCESSED:")
        for month, error in sorted(not_accessible.items()):
            print(f"  - {month}: {error}")
            print(f"    Sheet ID: {all_sheets[month]}")

    if no_data:
        print("\nSHEETS ACCESSIBLE BUT WITH NO/EMPTY DATA:")
        for month, reason in sorted(no_data.items()):
            print(f"  - {month}: {reason}")
            print(f"    Sheet ID: {all_sheets[month]}")

if __name__ == '__main__':
    main()
