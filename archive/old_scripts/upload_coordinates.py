#!/usr/bin/env python3
"""
Upload exact Google coordinates to the employee Google Sheet.
Matches by name and fills the Google Coordinates column.
"""

import csv
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as SACredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Sheet details
SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
SHEET_ID = 361249755
RANGE = "A1:Z1000"

# Load coordinates from CSV
def load_coordinates():
    """Load coordinates from CSV file."""
    coords = {}
    with open('output/GoogleCoordinates_ForSheet.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['Name'].strip()
            google_coord = row['Google Coordinates'].strip()
            coords[name] = google_coord
    return coords

def authenticate_sheets():
    """Authenticate with Google Sheets API."""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None

    # Try token.json first (cached credentials)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def get_sheet_data(service):
    """Get all data from the sheet."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    return result.get('values', [])

def find_google_coordinates_column(headers):
    """Find the column index for Google Coordinates."""
    for idx, header in enumerate(headers):
        if 'google' in header.lower() and 'coordinate' in header.lower():
            return idx
    return -1

def upload_coordinates():
    """Upload coordinates to the Google Sheet."""

    print("[AUTHENTICATING] Connecting to Google Sheets...")
    try:
        creds = authenticate_sheets()
        service = build('sheets', 'v4', credentials=creds)
        print("[SUCCESS] Authenticated with Google Sheets!")
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        print("[HINT] Make sure you have credentials.json in the current directory")
        return False

    # Load coordinates
    print("[LOADING] Reading coordinates from CSV...")
    coords = load_coordinates()
    print(f"[INFO] Loaded {len(coords)} coordinates")

    # Get current sheet data
    print("[FETCHING] Getting current sheet data...")
    sheet_data = get_sheet_data(service)

    if not sheet_data:
        print("[ERROR] Could not fetch sheet data")
        return False

    headers = sheet_data[0]
    print(f"[INFO] Found {len(headers)} columns")

    # Find Google Coordinates column
    coord_col_idx = find_google_coordinates_column(headers)
    if coord_col_idx == -1:
        print("[ERROR] Google Coordinates column not found!")
        print(f"[INFO] Available columns: {headers}")
        return False

    coord_col_letter = chr(65 + coord_col_idx)  # Convert to letter (A, B, C, etc.)
    print(f"[INFO] Found 'Google Coordinates' column at: {coord_col_letter}")

    # Find Name column
    name_col_idx = -1
    for idx, header in enumerate(headers):
        if header.strip().lower() == 'full name':
            name_col_idx = idx
            break

    if name_col_idx == -1:
        print("[WARNING] Could not find 'Full Name' column, trying 'Name'")
        for idx, header in enumerate(headers):
            if header.strip().lower() == 'name':
                name_col_idx = idx
                break

    if name_col_idx == -1:
        print("[ERROR] Could not find Name/Full Name column!")
        return False

    print(f"[INFO] Found 'Name' column at index {name_col_idx}")

    # Prepare updates
    updates = []
    matched = 0
    not_found = 0

    print("[PROCESSING] Matching names and preparing updates...")
    for row_idx, row in enumerate(sheet_data[1:], start=2):  # Start from row 2 (skip header)
        if row_idx > len(sheet_data):
            break

        if name_col_idx < len(row):
            name = row[name_col_idx].strip()

            if name in coords:
                coord = coords[name]
                cell_ref = f"{coord_col_letter}{row_idx}"
                updates.append({
                    'range': cell_ref,
                    'values': [[coord]]
                })
                matched += 1
                if matched <= 10:
                    print(f"  [{matched}] {name:35} -> {coord}")
            else:
                not_found += 1

    if matched > 10:
        print(f"  ... ({matched - 10} more)")

    print(f"\n[SUMMARY] Matched: {matched} | Not found: {not_found}")

    # Upload to sheet
    if updates:
        print(f"\n[UPLOADING] Adding {len(updates)} coordinates to your sheet...")

        try:
            body = {'data': updates, 'valueInputOption': 'RAW'}
            result = service.spreadsheets().values().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=body
            ).execute()

            print(f"[SUCCESS] Updated {result.get('totalUpdatedCells', 0)} cells!")
            print(f"\n[VERIFICATION] Check your Google Sheet:")
            print(f"  https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to upload: {e}")
            return False
    else:
        print("[WARNING] No coordinates to upload")
        return False

if __name__ == "__main__":
    upload_coordinates()
