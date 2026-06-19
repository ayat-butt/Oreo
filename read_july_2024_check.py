#!/usr/bin/env python3
"""Read July 2024 Excel to verify OPL data access"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
import pandas as pd
import io

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            import json
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except:
        return None

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    service = build('drive', 'v3', credentials=creds)

    # Search for July 2024 payroll file
    print("Searching for July 2024 payroll file...")

    # Try to find July 2024 file
    query = "name contains 'July' and name contains '2024' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType)',
        pageSize=10
    ).execute()

    files = results.get('files', [])

    if not files:
        print("No July 2024 Excel file found. Searching more broadly...")
        query = "name contains 'payroll' and name contains 'July'"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType)',
            pageSize=10
        ).execute()
        files = results.get('files', [])

    if files:
        print(f"\nFound {len(files)} file(s):")
        for file in files:
            print(f"  - {file['name']} (ID: {file['id']})")

            # Try to download and read
            try:
                # Get file content
                file_id = file['id']
                request = service.files().get_media(fileId=file_id)
                file_content = request.execute()

                # Read Excel
                df = pd.read_excel(io.BytesIO(file_content))

                print(f"\n  Sheet shape: {df.shape} (rows × columns)")
                print(f"  Columns: {list(df.columns)}")

                # Look for OPL sheet
                print(f"\n  First few rows:")
                print(df.head(10).to_string())

            except Exception as e:
                print(f"  Error reading file: {e}")
    else:
        print("No July 2024 file found")

if __name__ == '__main__':
    main()
