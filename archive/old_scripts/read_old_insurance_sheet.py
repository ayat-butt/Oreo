#!/usr/bin/env python3
"""Read old insurance data from the provided sheet."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def load_google_credentials():
    token_path = 'c:/Agent Oreo/token.json'
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    
    # Old insurance sheet ID from URL
    old_sheet_id = '1HjyeoWzsxkC_t2yzPgSn6qb_huvNYq7qvzHB2m-AxHI'
    
    print("Reading old insurance sheet...")
    try:
        # Read from "Orenda updated data" sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=old_sheet_id,
            range="'Orenda updated data'!A1:J100"
        ).execute()
        
        values = result.get('values', [])
        print(f"\nOld Insurance Data Structure:")
        print("-" * 120)
        print(f"Total rows: {len(values)}")
        
        # Show headers
        if values:
            print(f"\nHeaders: {values[0]}")
        
        # Count employees and dependents
        employee_count = 0
        dependent_count = 0
        
        print(f"\nFirst 15 data rows:")
        print("-" * 120)
        
        for idx, row in enumerate(values[1:16]):
            if row:
                emp_name = row[0] if row else ""
                emp_cnic = row[1] if len(row) > 1 else ""
                dependent = row[2] if len(row) > 2 else ""
                relationship = row[3] if len(row) > 3 else ""
                
                if not dependent:
                    employee_count += 1
                    print(f"EMP: {emp_name:<30} | CNIC: {emp_cnic:<20}")
                else:
                    dependent_count += 1
                    print(f"DEP: {emp_name:<30} | Dep: {dependent:<20} | Rel: {relationship}")
        
        # Count all
        total_emp = 0
        total_dep = 0
        for row in values[1:]:
            if row:
                dependent = row[2] if len(row) > 2 else ""
                if not dependent:
                    total_emp += 1
                else:
                    total_dep += 1
        
        print(f"\n\nTotal Summary:")
        print(f"  Total Employee Records: {total_emp}")
        print(f"  Total Dependent Records: {total_dep}")
        print(f"  Total Records: {total_emp + total_dep}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
