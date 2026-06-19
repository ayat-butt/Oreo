#!/usr/bin/env python3
"""Examine OWT format in detail to match exactly"""

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

spreadsheet_id = '1I1cd_67TyDjU7ACFOi7T7X_EzH88fNs8i_VeWVJUc5U'

try:
    # Get all sheets
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get('sheets', [])

    print("OWT Sample Format Analysis")
    print("="*150)

    # Get the first sheet data
    sheet_name = sheets[0]['properties']['title']

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!A1:M100"
    ).execute()

    rows = result.get('values', [])

    print(f"\nSheet: {sheet_name}\n")
    print("Row-by-row structure (showing all data):\n")

    for i, row in enumerate(rows[:100]):
        # Format row with column letters
        formatted_row = []
        for j, cell in enumerate(row):
            col_letter = chr(65 + j) if j < 26 else f"A{chr(65 + j - 26)}"
            formatted_row.append(f"{col_letter}: '{cell}'")

        print(f"Row {i:2d}: {' | '.join(formatted_row)}")

        if i > 80:
            break

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
