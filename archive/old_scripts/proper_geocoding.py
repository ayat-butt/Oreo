#!/usr/bin/env python3
"""
Proper geocoding with multiple fallbacks and error handling.
Uses geopy with Nominatim and gets REAL coordinates for each address.
"""

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import time

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
RANGE = "A1:I500"

def geocode_address(address):
    """Geocode a single address with retries."""

    geolocator = Nominatim(user_agent="oreo_employee_locations")

    # Ensure address has Pakistan context
    if "Pakistan" not in address and "Islamabad" not in address and "Rawalpindi" not in address:
        full_address = f"{address}, Islamabad, Pakistan"
    else:
        full_address = address

    try:
        location = geolocator.geocode(full_address, timeout=15)

        if location:
            return {
                "lat": round(location.latitude, 6),
                "lon": round(location.longitude, 6),
                "found": True
            }
        else:
            # Try with just sector/area name if full address fails
            parts = address.split(',')
            if len(parts) > 0:
                short_address = f"{parts[0].strip()}, Islamabad, Pakistan"
                try:
                    location = geolocator.geocode(short_address, timeout=10)
                    if location:
                        return {
                            "lat": round(location.latitude, 6),
                            "lon": round(location.longitude, 6),
                            "found": True
                        }
                except:
                    pass

            return {"lat": None, "lon": None, "found": False}

    except (GeocoderTimedOut, GeocoderServiceError):
        return {"lat": None, "lon": None, "found": False}

def geocode_all():
    """Geocode all employees and update sheet."""

    creds = Credentials.from_authorized_user_file('token.json')
    sheets = build('sheets', 'v4', credentials=creds)

    print("[FETCHING] Sheet data...")
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get('values', [])

    updates = []
    success = 0
    failed = 0

    print("[GEOCODING] Processing each address individually...\n")

    for row_idx, row in enumerate(values[1:], start=2):
        if not row or len(row) < 9:
            continue

        name = row[0].strip() if len(row) > 0 else ""
        address = row[5].strip() if len(row) > 5 else ""
        status = row[6].strip() if len(row) > 6 else ""

        if "needed" not in status.lower() or not address or not name:
            continue

        # Geocode this specific address
        print(f"[{success + failed + 1}] {name:30} | {address[:40]:40}", end=" -> ")

        result_coord = geocode_address(address)

        if result_coord["found"]:
            coordinates = f"{result_coord['lat']}, {result_coord['lon']}"
            updates.append({
                'range': f"I{row_idx}",
                'values': [[coordinates]]
            })
            success += 1
            print(f"[FOUND] {coordinates}")
        else:
            failed += 1
            print(f"[NO MATCH] Using default")
            # Keep previous value
            continue

        # Rate limiting to avoid service issues
        time.sleep(1)

    print(f"\n[RESULTS]")
    print(f"  Successfully geocoded: {success}")
    print(f"  Failed to geocode: {failed}")
    print(f"  Total: {success + failed}")

    # Upload
    if updates:
        print(f"\n[UPLOADING] {len(updates)} coordinates to sheet...")

        try:
            body = {'data': updates, 'valueInputOption': 'RAW'}
            result = sheets.spreadsheets().values().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=body
            ).execute()

            print(f"[SUCCESS] Updated {result.get('totalUpdatedCells', 0)} cells!")
            print(f"\nSheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")

        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")

if __name__ == "__main__":
    geocode_all()
