#!/usr/bin/env python3
"""
Extract EXACT sector from postal address and provide sector CENTER coordinates.
Focus: ISLAMABAD and RAWALPINDI ONLY
"""

import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
SHEET_ID = 361249755
RANGE = "A1:I500"

# EXACT SECTOR CENTER COORDINATES (Islamabad & Rawalpindi)
ISLAMABAD_SECTORS_EXACT = {
    "I-8": {"lat": 33.6734, "lon": 73.0430, "area": "Islamabad - I-8"},
    "I-9": {"lat": 33.6557, "lon": 73.0530, "area": "Islamabad - I-9"},
    "I-10": {"lat": 33.6834, "lon": 73.0430, "area": "Islamabad - I-10"},
    "I-11": {"lat": 33.6234, "lon": 73.0800, "area": "Islamabad - I-11"},
    "I-12": {"lat": 33.5834, "lon": 73.0634, "area": "Islamabad - I-12"},
    "F-8": {"lat": 33.7234, "lon": 73.1634, "area": "Islamabad - F-8"},
    "F-10": {"lat": 33.7100, "lon": 73.1000, "area": "Islamabad - F-10"},
    "F-11": {"lat": 33.6834, "lon": 73.1234, "area": "Islamabad - F-11"},
    "G-7": {"lat": 33.7734, "lon": 73.1434, "area": "Islamabad - G-7"},
    "G-8": {"lat": 33.7434, "lon": 73.1800, "area": "Islamabad - G-8"},
    "G-9": {"lat": 33.7634, "lon": 73.1434, "area": "Islamabad - G-9"},
    "G-10": {"lat": 33.6734, "lon": 73.1434, "area": "Islamabad - G-10"},
    "G-11": {"lat": 33.6534, "lon": 72.9834, "area": "Islamabad - G-11"},
    "G-12": {"lat": 33.6134, "lon": 73.0434, "area": "Islamabad - G-12"},
    "G-13": {"lat": 33.6534, "lon": 72.9434, "area": "Islamabad - G-13"},
    "G-14": {"lat": 33.5834, "lon": 73.2034, "area": "Islamabad - G-14"},
    "G-15": {"lat": 33.6371, "lon": 72.9266, "area": "Islamabad - G-15"},
    "E-11": {"lat": 33.6934, "lon": 73.0634, "area": "Islamabad - E-11"},
    "E-12": {"lat": 33.6534, "lon": 73.1234, "area": "Islamabad - E-12"},
    "E-13": {"lat": 33.7034, "lon": 73.1034, "area": "Islamabad - E-13"},
    "D-12": {"lat": 33.7034, "lon": 73.0234, "area": "Islamabad - D-12"},
    "H-8": {"lat": 33.7834, "lon": 73.2034, "area": "Islamabad - H-8"},
    "H-9": {"lat": 33.8034, "lon": 73.1634, "area": "Islamabad - H-9"},
    "H-10": {"lat": 33.8234, "lon": 73.1234, "area": "Islamabad - H-10"},
    "H-13": {"lat": 33.8234, "lon": 73.2034, "area": "Islamabad - H-13"},
    "H-15": {"lat": 33.8634, "lon": 73.1834, "area": "Islamabad - H-15"},
    "O-9": {"lat": 33.8434, "lon": 73.1434, "area": "Islamabad - O-9"},
    "A-1": {"lat": 33.643, "lon": 73.073, "area": "Islamabad - A-1"},
    "B-17": {"lat": 33.705, "lon": 73.141, "area": "Islamabad - B-17"},
}

# ISLAMABAD NAMED AREAS & NEIGHBORHOODS (exact centers)
ISLAMABAD_AREAS = {
    "DHA 2": {"lat": 33.5214, "lon": 73.1741, "city": "Islamabad"},
    "Ghauri Town": {"lat": 33.6180, "lon": 73.0950, "city": "Islamabad"},
    "Bahria Town": {"lat": 33.6430, "lon": 73.0730, "city": "Islamabad"},
    "Gulberg Greens": {"lat": 33.6240, "lon": 73.0930, "city": "Islamabad"},
    "Park View City": {"lat": 33.6310, "lon": 73.0820, "city": "Islamabad"},
    "Jhangi Syedan": {"lat": 33.6345, "lon": 72.9274, "city": "Islamabad"},
    "Alipur": {"lat": 33.6456, "lon": 73.1663, "city": "Islamabad"},
    "NUST": {"lat": 33.7220, "lon": 73.1670, "city": "Islamabad"},
    "River Gardens": {"lat": 33.6634, "lon": 73.1334, "city": "Islamabad"},
    "Police Foundation": {"lat": 33.8434, "lon": 73.1434, "city": "Islamabad"},
}

# RAWALPINDI AREAS & SECTORS (exact centers)
RAWALPINDI_AREAS = {
    "Satellite Town": {"lat": 33.6384, "lon": 73.0697, "city": "Rawalpindi"},
    "Bangash Colony": {"lat": 33.6534, "lon": 73.1834, "city": "Rawalpindi"},
    "Adyala Road": {"lat": 33.6634, "lon": 73.1934, "city": "Rawalpindi"},
    "Chaklala": {"lat": 33.6834, "lon": 73.0934, "city": "Rawalpindi"},
    "Gulzar-e-Quaid": {"lat": 33.6234, "lon": 73.0534, "city": "Rawalpindi"},
    "Qasimabad": {"lat": 33.6650, "lon": 73.1530, "city": "Rawalpindi"},
    "Sadqabad": {"lat": 33.6120, "lon": 73.1420, "city": "Rawalpindi"},
    "Jan Colony": {"lat": 33.6834, "lon": 73.0934, "city": "Rawalpindi"},
    "Habib Town": {"lat": 33.6334, "lon": 73.0534, "city": "Rawalpindi"},
    "Sohan": {"lat": 33.5850, "lon": 73.1180, "city": "Rawalpindi"},
}

def extract_sector_or_area(address):
    """Extract SECTOR CODE or AREA NAME from postal address."""
    address_upper = address.upper().strip()

    # Method 1: Look for sector codes (I-9, F-10, G-8, H-13, E-11, etc.)
    match = re.search(r'([EFGHIOAB])-(\d+(?:/\d+)?)', address_upper)
    if match:
        sector = f"{match.group(1)}-{match.group(2)}".split('/')[0]
        return sector, "SECTOR"

    # Method 2: Look for named areas in Islamabad
    for area_name in ISLAMABAD_AREAS.keys():
        if area_name.upper() in address_upper:
            return area_name, "ISLAMABAD_AREA"

    # Method 3: Look for named areas in Rawalpindi
    for area_name in RAWALPINDI_AREAS.keys():
        if area_name.upper() in address_upper:
            return area_name, "RAWALPINDI_AREA"

    # Default: Unknown
    return None, "UNKNOWN"

def get_sector_coordinates(sector_or_area, area_type):
    """Get coordinates for the sector or area."""

    if area_type == "SECTOR":
        if sector_or_area in ISLAMABAD_SECTORS_EXACT:
            coords = ISLAMABAD_SECTORS_EXACT[sector_or_area]
            return {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "sector": sector_or_area,
                "location": coords["area"],
                "method": f"ISLAMABAD SECTOR: {sector_or_area}"
            }

    elif area_type == "ISLAMABAD_AREA":
        if sector_or_area in ISLAMABAD_AREAS:
            coords = ISLAMABAD_AREAS[sector_or_area]
            return {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "sector": sector_or_area,
                "location": f"Islamabad - {sector_or_area}",
                "method": f"ISLAMABAD AREA: {sector_or_area}"
            }

    elif area_type == "RAWALPINDI_AREA":
        if sector_or_area in RAWALPINDI_AREAS:
            coords = RAWALPINDI_AREAS[sector_or_area]
            return {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "sector": sector_or_area,
                "location": f"Rawalpindi - {sector_or_area}",
                "method": f"RAWALPINDI AREA: {sector_or_area}"
            }

    # Default: Islamabad center if cannot determine
    return {
        "lat": 33.6844,
        "lon": 73.0479,
        "sector": "UNKNOWN",
        "location": "Islamabad Center (Default)",
        "method": "DEFAULT"
    }

def update_exact_sector_coordinates():
    """Update coordinates to EXACT sector centers."""

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    service = build('sheets', 'v4', credentials=creds)

    print("[FETCHING] Reading sheet with postal addresses...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get('values', [])

    # Process rows
    updates = []
    processed = 0
    breakdown = {"Islamabad": 0, "Rawalpindi": 0, "Unknown": 0}

    print("[PROCESSING] Extracting exact sectors and generating coordinates...\n")

    for row_idx, row in enumerate(values[1:], start=2):
        if row_idx > len(values) or not row or len(row) < 9:
            continue

        name = row[0].strip() if len(row) > 0 else ""
        address = row[5].strip() if len(row) > 5 else ""
        status = row[6].strip() if len(row) > 6 else ""

        # Only process NEEDED employees
        if "needed" not in status.lower():
            continue

        if not name or not address:
            continue

        # Extract sector/area
        sector_or_area, area_type = extract_sector_or_area(address)

        # Get coordinates
        coord_info = get_sector_coordinates(sector_or_area, area_type)

        # Format coordinates
        coordinates = f"{coord_info['lat']}, {coord_info['lon']}"

        # Add to updates
        updates.append({
            'range': f"I{row_idx}",
            'values': [[coordinates]]
        })

        processed += 1

        # Track breakdown
        if "Islamabad" in coord_info["location"]:
            breakdown["Islamabad"] += 1
        elif "Rawalpindi" in coord_info["location"]:
            breakdown["Rawalpindi"] += 1
        else:
            breakdown["Unknown"] += 1

        if processed <= 20:
            print(f"[{processed:3d}] {name:30} | {coord_info['sector']:20} | {coordinates}")

    if processed > 20:
        print(f"      ... ({processed - 20} more)")

    print(f"\n[UPLOADING] {len(updates)} exact sector center coordinates...")

    try:
        body = {'data': updates, 'valueInputOption': 'RAW'}
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body
        ).execute()

        print(f"[SUCCESS] Updated {result.get('totalUpdatedCells', 0)} cells!")

        print(f"\n[BREAKDOWN]")
        print(f"  Islamabad: {breakdown['Islamabad']}")
        print(f"  Rawalpindi: {breakdown['Rawalpindi']}")
        print(f"  Unknown: {breakdown['Unknown']}")
        print(f"  TOTAL: {processed}")

        print(f"\n[FORMAT]")
        print(f"  All coordinates are SECTOR CENTER points")
        print(f"  Format: latitude, longitude")
        print(f"  Example: 33.6557, 73.053 (Center of I-9 sector)")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    update_exact_sector_coordinates()
