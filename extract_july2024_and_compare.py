#!/usr/bin/env python3
"""Extract July 2024 OPL data and compare with November 2024"""

import requests
import pandas as pd
from io import BytesIO
import json

def read_excel_from_google_drive(sheet_id):
    """Download and read Excel file from Google Drive"""
    try:
        download_url = f"https://docs.google.com/spreadsheets/export?id={sheet_id}&exportFormat=xlsx"
        response = requests.get(download_url, timeout=30)

        if response.status_code == 200:
            excel_file = BytesIO(response.content)
            xls = pd.ExcelFile(excel_file)
            sheet_names = xls.sheet_names

            # Read first sheet
            df = pd.read_excel(excel_file, sheet_name=sheet_names[0])
            return df
        else:
            print(f"Failed: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_employees(df):
    """Extract employee data from dataframe"""
    employees = {}

    # Find employee name column
    name_col = None
    dept_col = None
    designation_col = None
    salary_col = None

    for col in df.columns:
        col_lower = str(col).lower().strip()
        if 'employee' in col_lower and 'name' in col_lower:
            name_col = col
        elif 'depart' in col_lower:
            dept_col = col
        elif 'designation' in col_lower:
            designation_col = col
        elif 'gross' in col_lower and 'salary' in col_lower:
            salary_col = col

    if name_col is None:
        print("Could not find employee name column")
        return employees

    # Extract employees
    for idx, row in df.iterrows():
        name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
        if not name or name.lower() == 'nan' or len(name) < 3 or 'total' in name.lower():
            continue

        dept = str(row[dept_col]).strip() if dept_col and pd.notna(row[dept_col]) else ""
        designation = str(row[designation_col]).strip() if designation_col and pd.notna(row[designation_col]) else ""
        salary = str(row[salary_col]).strip() if salary_col and pd.notna(row[salary_col]) else ""

        employees[name] = {
            'department': dept,
            'designation': designation,
            'salary': salary
        }

    return employees

def get_november_employees():
    """Get November 2024 employees from Sheets API"""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())

        service = build('sheets', 'v4', credentials=creds)

        sheet_id = '1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA'
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="'OPL'!A1:Z500"
        ).execute()

        rows = result.get('values', [])

        # Find header
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
        designation_col = None
        salary_col = None

        for col_idx, header in enumerate(headers):
            h = str(header).lower()
            if 'employee' in h and name_col is None:
                name_col = col_idx
            elif 'depart' in h:
                dept_col = col_idx
            elif 'designation' in h:
                designation_col = col_idx
            elif 'gross' in h and 'salary' in h:
                salary_col = col_idx

        employees = {}
        for row_idx in range(header_row + 1, len(rows)):
            row = rows[row_idx]
            if not row or len(row) < 2:
                continue

            name = row[name_col].strip() if name_col and name_col < len(row) else ''
            if not name or 'total' in name.lower() or len(name) < 3:
                continue

            dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
            designation = row[designation_col].strip() if designation_col and designation_col < len(row) else ''
            salary = row[salary_col].strip() if salary_col and salary_col < len(row) else ''

            employees[name] = {
                'department': dept,
                'designation': designation,
                'salary': salary
            }

        return employees

    except Exception as e:
        print(f"Error getting November data: {e}")
        return {}

print("="*120)
print("JULY 2024 vs NOVEMBER 2024 ANALYSIS")
print("="*120)

# Read July 2024
print("\nReading July 2024 data...")
july_df = read_excel_from_google_drive('1tIKIU0LKCR2YYuCS0u0lb_Gr-rDm6ks_')
july_employees = extract_employees(july_df) if july_df is not None else {}
print(f"Found {len(july_employees)} employees in July 2024")

# Get November 2024
print("\nReading November 2024 data...")
november_employees = get_november_employees()
print(f"Found {len(november_employees)} employees in November 2024")

# Compare
july_names = set(july_employees.keys())
november_names = set(november_employees.keys())

# Who was in July but not in November (leavers)
july_only = july_names - november_names
print(f"\n[JULY ONLY - Left before November]: {len(july_only)} employees")
for name in sorted(july_only)[:20]:
    print(f"  - {name}")
if len(july_only) > 20:
    print(f"  ... and {len(july_only) - 20} more")

# Who was in November but not in July (new joiners)
november_only = november_names - july_names
print(f"\n[NOVEMBER ONLY - New joiners]: {len(november_only)} employees")
for name in sorted(november_only)[:20]:
    print(f"  + {name}")
if len(november_only) > 20:
    print(f"  ... and {len(november_only) - 20} more")

# Who was in both (continuing employees)
both = july_names & november_names
print(f"\n[IN BOTH MONTHS - Continuing employees]: {len(both)} employees")
for name in sorted(both)[:20]:
    print(f"  * {name}")
if len(both) > 20:
    print(f"  ... and {len(both) - 20} more")

# Save detailed report
with open('output/JULY_NOVEMBER_COMPARISON.txt', 'w', encoding='utf-8') as f:
    f.write("="*120 + "\n")
    f.write("JULY 2024 vs NOVEMBER 2024 OPL ANALYSIS\n")
    f.write("="*120 + "\n\n")

    f.write(f"SUMMARY:\n")
    f.write(f"  July 2024 employees: {len(july_employees)}\n")
    f.write(f"  November 2024 employees: {len(november_employees)}\n")
    f.write(f"  Continuing (in both): {len(both)}\n")
    f.write(f"  Left (July only): {len(july_only)}\n")
    f.write(f"  New joiners (November only): {len(november_only)}\n\n")

    f.write("JULY 2024 EMPLOYEES WHO LEFT BEFORE NOVEMBER:\n")
    f.write("-"*120 + "\n")
    for name in sorted(july_only):
        emp = july_employees[name]
        f.write(f"{name:<40} | Dept: {emp['department']:<40}\n")

    f.write(f"\n\nNEW JOINERS IN NOVEMBER 2024:\n")
    f.write("-"*120 + "\n")
    for name in sorted(november_only):
        emp = november_employees[name]
        f.write(f"{name:<40} | Dept: {emp['department']:<40}\n")

    f.write(f"\n\nCONTINUING EMPLOYEES (IN BOTH MONTHS):\n")
    f.write("-"*120 + "\n")
    for name in sorted(both):
        emp = july_employees[name]
        f.write(f"{name:<40} | Dept: {emp['department']:<40}\n")

print("\n" + "="*120)
print("Report saved to output/JULY_NOVEMBER_COMPARISON.txt")
print("="*120)
