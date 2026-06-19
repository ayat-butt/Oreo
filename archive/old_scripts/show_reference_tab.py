#!/usr/bin/env python3
"""Show what's in the reference tab after comprehensive cross-check."""

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
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Get reference tab data
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="'Data from Old Insurance Sheet'!A:D"
    ).execute()

    values = result.get('values', [])
    
    print("\n" + "="*120)
    print("REFERENCE TAB - 23 MISSING RECORDS (Employees not in 2026 Markaz)")
    print("="*120 + "\n")
    
    print(f"{'Employee Name':<35} {'CNIC':<20} {'Insured Person':<35} {'Relation':<15}")
    print("-" * 120)

    for idx, row in enumerate(values[1:]):
        if row:
            emp_name = (row[0] if row[0] else "")[:35]
            cnic = (row[1] if len(row) > 1 else "")[:20]
            insured = (row[2] if len(row) > 2 else "")[:35]
            relation = (row[3] if len(row) > 3 else "")[:15]
            
            try:
                print(f"{emp_name:<35} {cnic:<20} {insured:<35} {relation:<15}")
            except:
                print(f"[Non-ASCII] {cnic:<20}")

    print("\n" + "="*120)
    print(f"Total Records: {len(values) - 1}")
    print("="*120)

if __name__ == "__main__":
    main()
