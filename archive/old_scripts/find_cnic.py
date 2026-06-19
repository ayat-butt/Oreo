#!/usr/bin/env python3
"""Find where a specific CNIC appears."""

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
    search_cnic = '6110198676046'
    search_name = 'tameem fatima'
    
    print(f"Searching for CNIC: {search_cnic} and Name: {search_name}\n")
    
    # Search in old insurance sheet
    print("="*100)
    print("Searching in OLD INSURANCE SHEET (Orenda updated data)...")
    print("="*100)
    
    try:
        old_sheet_id = '1HjyeoWzsxkC_t2yzPgSn6qb_huvNYq7qvzHB2m-AxHI'
        result = service.spreadsheets().values().get(
            spreadsheetId=old_sheet_id,
            range="'Orenda updated data'!A:J"
        ).execute()
        
        values = result.get('values', [])
        found_old = False
        
        for idx, row in enumerate(values):
            if not row:
                continue
            row_str = ' '.join([str(cell).lower() for cell in row])
            
            if search_cnic in row_str or search_name in row_str:
                found_old = True
                print(f"Row {idx}: {row[:4]}")
        
        if not found_old:
            print("NOT FOUND in old insurance sheet")
    except Exception as e:
        print(f"Error: {e}")
    
    # Search in current 2026 sheet
    print("\n" + "="*100)
    print("Searching in 2026 MARKAZ SHEET (Sheet1)...")
    print("="*100)
    
    try:
        markaz_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'
        result = service.spreadsheets().values().get(
            spreadsheetId=markaz_sheet_id,
            range='Sheet1!A:C'
        ).execute()
        
        values = result.get('values', [])
        found_markaz = False
        
        for idx, row in enumerate(values):
            if not row:
                continue
            row_str = ' '.join([str(cell).lower() for cell in row])
            
            if search_cnic in row_str or search_name in row_str:
                found_markaz = True
                print(f"Row {idx}: {row[:3]}")
        
        if not found_markaz:
            print("NOT FOUND in 2026 Markaz sheet")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
