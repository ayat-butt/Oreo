#!/usr/bin/env python3
"""Extract May 2025 employee data for joiners/leavers sheet"""

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

creds = load_credentials()
service = build('sheets', 'v4', credentials=creds)

# May 2025 sheet
may_sheet_id = '1uhAxR4UCrY5OOmQHgfdpqOS_M3QeIUBt66YtojpRHD0'

try:
    result = service.spreadsheets().values().get(
        spreadsheetId=may_sheet_id,
        range="'OPL'!A1:Z500"
    ).execute()
    
    rows = result.get('values', [])
    
    # Find header row
    header_row = None
    for i, row in enumerate(rows[:10]):
        if row and any('employee' in str(cell).lower() for cell in row):
            header_row = i
            break
    
    if header_row is None:
        print("No header found")
    else:
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
            elif 'designation' in h or 'title' in h:
                designation_col = col_idx
            elif 'gross' in h and 'salary' in h:
                salary_col = col_idx
        
        print("May 2025 OPL Employees:")
        print("="*120)
        
        employees = {}
        for row_idx in range(header_row + 1, len(rows)):
            row = rows[row_idx]
            if not row or len(row) < 2:
                continue
            
            name = row[name_col].strip() if name_col and name_col < len(row) else ''
            if not name or name == '' or name.isdigit() or 'total' in name.lower():
                continue
            if len(name) < 3 or not any(c.isalpha() for c in name):
                continue
            
            dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
            designation = row[designation_col].strip() if designation_col and designation_col < len(row) else ''
            salary = row[salary_col].strip() if salary_col and salary_col < len(row) else ''
            
            employees[name] = {
                'department': dept,
                'designation': designation,
                'salary': salary
            }
            print(f"{name:<40} | Dept: {dept:<50} | Desig: {designation:<40} | Salary: {salary}")
        
        print(f"\nTotal: {len(employees)} employees")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
