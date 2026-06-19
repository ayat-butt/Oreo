#!/usr/bin/env python3
"""
Update coordinates to match Buscaro tracker format:
- Coordinates: "latitude, longitude" (with space after comma)
- Google Maps Links: https://maps.google.com/?q=latitude,longitude
"""

import csv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
RANGE = "A1:Z100"

def load_coordinates():
    """Load coordinates from CSV."""
    coords = {}
    with open('output/GoogleCoordinates_ForSheet.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['Name'].strip()
            # Extract just the numbers
            parts = row['Google Coordinates'].split(',')
            if len(parts) >= 2:
                lat = parts[0].strip()
                lon = parts[1].strip()
                # Buscaro format: "latitude, longitude" (with space)
                coords[name] = {
                    'coordinates': f"{lat}, {lon}",
                    'maps_link': f"https://maps.google.com/?q={lat},{lon}"
                }
    return coords

def update_coordinates():
    """Update coordinates in Buscaro format."""

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds:
        print("[ERROR] No authentication")
        return False

    service = build('sheets', 'v4', credentials=creds)

    # Load coordinates
    print("[LOADING] Coordinates...")
    coords = load_coordinates()
    print(f"[INFO] Loaded {len(coords)} coordinates")

    # Get sheet data
    print("[FETCHING] Sheet data...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get('values', [])
    headers = values[0]

    # Find columns
    coord_col_idx = -1
    maps_col_idx = -1
    name_col_idx = -1

    for idx, header in enumerate(headers):
        if 'google' in header.lower() and 'coordinate' in header.lower():
            coord_col_idx = idx
        if 'google' in header.lower() and ('map' in header.lower() or 'link' in header.lower()):
            maps_col_idx = idx
        if header.lower() in ['full name', 'name']:
            name_col_idx = idx

    if coord_col_idx == -1:
        print("[ERROR] Google Coordinates column not found")
        return False

    if name_col_idx == -1:
        print("[ERROR] Name column not found")
        return False

    coord_col_letter = chr(65 + coord_col_idx)

    print(f"[INFO] Coordinates column: {coord_col_letter}")
    if maps_col_idx != -1:
        maps_col_letter = chr(65 + maps_col_idx)
        print(f"[INFO] Maps link column: {maps_col_letter}")

    # Prepare updates
    updates = []
    matched = 0

    print(f"\n[FORMATTING] Converting to Buscaro format...")
    for row_idx, row in enumerate(values[1:], start=2):
        if row_idx > len(values):
            break

        if name_col_idx < len(row):
            name = row[name_col_idx].strip()

            if name in coords:
                # Update coordinates column
                cell_ref = f"{coord_col_letter}{row_idx}"
                coord_value = coords[name]['coordinates']
                updates.append({
                    'range': cell_ref,
                    'values': [[coord_value]]
                })

                # Update maps link column if it exists
                if maps_col_idx != -1:
                    maps_cell_ref = f"{maps_col_letter}{row_idx}"
                    maps_link = coords[name]['maps_link']
                    updates.append({
                        'range': maps_cell_ref,
                        'values': [[maps_link]]
                    })

                matched += 1
                if matched <= 10:
                    print(f"  [{matched}] {name:35} -> {coord_value}")

    if matched > 10:
        print(f"  ... ({matched - 10} more)")

    print(f"\n[UPLOADING] {len(updates)} updates to your sheet...")

    try:
        body = {'data': updates, 'valueInputOption': 'RAW'}
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body
        ).execute()

        print(f"[SUCCESS] Updated {result.get('totalUpdatedCells', 0)} cells!")
        print(f"\n[FORMAT SAMPLE]")
        print(f"  Coordinates: {list(coords.values())[0]['coordinates']}")
        print(f"  Maps Link:   {list(coords.values())[0]['maps_link']}")
        print(f"\n[VERIFICATION] Check your sheet:")
        print(f"  https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    update_coordinates()
