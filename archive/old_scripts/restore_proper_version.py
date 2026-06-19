#!/usr/bin/env python3
"""Restore to version before bank details were added."""

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

    drive_service = build('drive', 'v3', credentials=creds)
    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    print("\nRESTORATION URGENT - Data Overwrite Detected!\n")
    print("=" * 100)
    print("\nYou MUST restore from version history immediately:")
    print("\n1. Go to: https://docs.google.com/spreadsheets/d/1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s/edit")
    print("\n2. Click version history (clock icon, top right)")
    print("\n3. Find version from 07:34 (ID: 47) - BEFORE bank update")
    print("\n4. Click 'Restore this version'")
    print("\n5. Click 'Restore' to confirm")
    print("\n" + "=" * 100)
    
    print("\nChecking available revisions...\n")
    
    try:
        revisions = drive_service.revisions().list(
            fileId=insurance_sheet_id,
            fields='revisions(id,modifiedTime)',
            pageSize=10
        ).execute()

        revisions_list = revisions.get('revisions', [])
        
        print("Available Versions (newest first):")
        for idx, rev in enumerate(revisions_list):
            print(f"  [{rev['id']}] {rev['modifiedTime']}")
        
        print("\nRESTORE TO: Revision ID 47 (07:34)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
