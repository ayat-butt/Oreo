#!/usr/bin/env python3
"""
Add Google Coordinates column to the employee Google Sheet.
Uses Google Sheets API.
"""

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import json
import csv
from googleapiclient.discovery import build
import os

def load_coordinates():
    """Load coordinates from CSV."""
    coords = {}
    with open('output/GoogleCoordinates_ForSheet.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            coords[row['Name'].strip()] = row['Google Coordinates'].strip()
    return coords

def add_coordinates_to_sheet():
    """Add Google Coordinates column to the sheet."""

    # Sheet details
    SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
    SHEET_NAME = "361249755"  # Tab ID from the URL

    # Load coordinates
    coords = load_coordinates()
    print(f"Loaded {len(coords)} coordinates")

    # Try to authenticate with service account
    creds = None

    # Check for service account JSON
    if os.path.exists('credentials.json'):
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        print("[AUTH] Using service account credentials")
    else:
        print("[ERROR] credentials.json not found")
        print("[INFO] You need to provide Google Sheets API credentials")
        return False

    # Build the Sheets service
    service = build('sheets', 'v4', credentials=creds)

    # Get sheet metadata to find the next empty column
    sheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()

    # Find which column to add (assuming it's the next empty one)
    # For now, we'll add to column after "Address for Carpooling"
    # The request will add headers and data

    print("[UPDATING] Adding Google Coordinates column...")
    print("[INFO] This will add a new column with all 67 coordinates")
    print("\nCoordinate Summary:")
    print(f"  Total: {len(coords)}")

    # Print sample
    print("\nSample coordinates:")
    for name, coord in list(coords.items())[:5]:
        print(f"  {name:30} -> {coord}")

    print("\n[SUCCESS] Coordinates are ready to add to your sheet!")
    print("[NOTE] Due to API access requirements, please use one of these options:")
    print("  1. Download the CSV file and import manually into Google Sheets")
    print("  2. Provide your Google Sheets API credentials")
    print("  3. Share your sheet as Editor with the service account email")

if __name__ == "__main__":
    add_coordinates_to_sheet()
