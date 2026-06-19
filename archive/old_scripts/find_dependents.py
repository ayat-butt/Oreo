#!/usr/bin/env python3
"""Find who Beena Zahir and Zahir Ahmad are dependents of."""

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
    
    print("Searching for dependents: 'Beena Zahir' and 'Zahir Ahmad'\n")
    print("=" * 120)
    
    # Search in 2026 Markaz sheet
    print("\n2026 MARKAZ SHEET (Sheet1):")
    print("-" * 120)
    
    markaz_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'
    result = service.spreadsheets().values().get(
        spreadsheetId=markaz_sheet_id,
        range='Sheet1!A:D'
    ).execute()
    
    values = result.get('values', [])
    found_markaz = False
    
    for idx, row in enumerate(values):
        if not row:
            continue
        row_str = ' '.join([str(cell).lower() for cell in row if cell])

        if 'beena zahir' in row_str or 'zahir ahmad' in row_str:
            found_markaz = True
            emp_name = row[1] if len(row) > 1 else ""
            dependent = row[2] if len(row) > 2 else ""
            relation = row[3] if len(row) > 3 else ""
            try:
                print(f"Row {idx}: Employee={emp_name} | Dependent={dependent} | Relation={relation}")
            except:
                print(f"Row {idx}: [Found match - non-ASCII characters]")
    
    if not found_markaz:
        print("NOT FOUND in 2026 Markaz sheet")
    
    # Search in old insurance sheet
    print("\n" + "=" * 120)
    print("OLD INSURANCE SHEET (Orenda updated data):")
    print("-" * 120)
    
    old_sheet_id = '1HjyeoWzsxkC_t2yzPgSn6qb_huvNYq7qvzHB2m-AxHI'
    result = service.spreadsheets().values().get(
        spreadsheetId=old_sheet_id,
        range="'Orenda updated data'!A:D"
    ).execute()
    
    values = result.get('values', [])
    found_old = False
    
    for idx, row in enumerate(values):
        if not row:
            continue
        row_str = ' '.join([str(cell).lower() for cell in row if cell])

        if 'beena zahir' in row_str or 'zahir ahmad' in row_str:
            found_old = True
            emp_name = row[0] if len(row) > 0 else ""
            cnic = row[1] if len(row) > 1 else ""
            insured = row[2] if len(row) > 2 else ""
            relation = row[3] if len(row) > 3 else ""
            try:
                print(f"Row {idx}: Employee={emp_name} | CNIC={cnic} | Insured={insured} | Relation={relation}")
            except:
                print(f"Row {idx}: [Found match - non-ASCII characters]")
    
    if not found_old:
        print("NOT FOUND in old insurance sheet")

if __name__ == "__main__":
    main()
