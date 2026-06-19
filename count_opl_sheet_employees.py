#!/usr/bin/env python3
"""Count total employees in OPL sheet"""

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

sheet_id = '1gSCNdfIRMf5NyaT_WvDrI2J1SwTydlj8MSuZlL-z4yU'

try:
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Sheet1!A1:G1000'
    ).execute()
    
    rows = result.get('values', [])
    
    print("OPL SHEET SUMMARY")
    print("="*100)
    print(f"\nSheet Title: {rows[1][1] if len(rows) > 1 else 'N/A'}")
    print(f"\nHeader Row (Row 3):")
    if len(rows) > 2:
        print(f"  {rows[2]}")
    
    # Count employees (rows 4 onwards)
    employee_rows = rows[3:]  # Skip first 3 rows (blank, title, header)
    
    # Count non-empty rows
    employees = []
    for row in employee_rows:
        if row and len(row) > 1 and row[1].strip():  # Check if name column is not empty
            employees.append(row)
    
    print(f"\n\nTOTAL EMPLOYEES: {len(employees)}")
    
    print("\n\nFIRST 10 EMPLOYEES:")
    print("-"*100)
    for i, emp in enumerate(employees[:10], 1):
        name = emp[1] if len(emp) > 1 else ""
        dept = emp[2] if len(emp) > 2 else ""
        joining = emp[4] if len(emp) > 4 else ""
        leaving = emp[5] if len(emp) > 5 else ""
        print(f"{i:2d}. {name:<35} | Joining: {joining:<15} | Leaving: {leaving:<20}")
    
    print("\n\nLAST 10 EMPLOYEES:")
    print("-"*100)
    for i, emp in enumerate(employees[-10:], len(employees) - 9):
        name = emp[1] if len(emp) > 1 else ""
        dept = emp[2] if len(emp) > 2 else ""
        joining = emp[4] if len(emp) > 4 else ""
        leaving = emp[5] if len(emp) > 5 else ""
        print(f"{i:2d}. {name:<35} | Joining: {joining:<15} | Leaving: {leaving:<20}")
    
    # Analyze joining months
    joining_months = {}
    leaving_months = {}
    
    for emp in employees:
        joining = emp[4] if len(emp) > 4 else ""
        leaving = emp[5] if len(emp) > 5 else ""
        
        if joining:
            joining_months[joining] = joining_months.get(joining, 0) + 1
        if leaving:
            leaving_months[leaving] = leaving_months.get(leaving, 0) + 1
    
    print("\n\nJOINERS BY MONTH:")
    print("-"*100)
    for month in sorted(joining_months.keys()):
        print(f"  {month}: {joining_months[month]} employees")
    
    print("\n\nLEAVERS BY MONTH:")
    print("-"*100)
    for month in sorted(leaving_months.keys()):
        print(f"  {month}: {leaving_months[month]} employees")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
