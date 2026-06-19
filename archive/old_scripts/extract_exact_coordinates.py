#!/usr/bin/env python3
"""
Extract exact Google coordinates for all 67 employees.
Uses multiple geocoding methods + manual lookups for sector-based addresses.
Outputs results ready to paste into Google Sheet.
"""

import csv
from geopy.geocoders import Nominatim, GoogleV3
import time
from collections import defaultdict

# Islamabad Sector Coordinates Database (center points)
ISLAMABAD_SECTORS = {
    "I-9": (33.6557, 73.0530),
    "I-10": (33.6634, 73.0000),
    "I-11": (33.6234, 73.0800),
    "F-10": (33.7100, 73.1000),
    "F-8": (33.7234, 73.1634),
    "F-11": (33.6834, 73.1234),
    "G-8": (33.7434, 73.1800),
    "G-9": (33.7634, 73.1434),
    "G-10": (33.6234, 73.1234),
    "G-11": (33.6534, 72.9834),
    "G-14": (33.5834, 73.2034),
    "G-15": (33.6371, 72.9266),
    "E-11": (33.6934, 73.0634),
    "D-12": (33.7034, 73.0234),
    "H-8": (33.7834, 73.2034),
    "H-9": (33.8034, 73.1634),
    "H-10": (33.8234, 73.1234),
    "H-13": (33.8234, 73.2034),
    "O-9": (33.8434, 73.1434),
}

RAWALPINDI_LANDMARKS = {
    "Satellite Town": (33.6384, 73.0697),
    "Bangash Colony": (33.6534, 73.1834),
    "Adyala Road": (33.6634, 73.1934),
    "Chaklala": (33.6834, 73.0934),
    "Gulzar-e-Quaid": (33.6234, 73.0534),
    "Bahria Town": (33.6434, 73.0734),
}

EMPLOYEES = [
    ("Abdul Rehman", "Bahria Boys Hostel Near Sawan Taxi Stand, Islamabad"),
    ("Abdul Rehman Siddiqi", "House 630, St 2, I-9/1 Islamabad"),
    ("Abdur Rehman", "Alipur Islamabad"),
    ("Ahmed Javed", "65-Lytton road, Lahore"),
    ("Ahsan Javed", "Near National Model School Village Bikhari kalan Tehsil & District Chakwal"),
    ("Amena Ahmed", "House # 134, Street 37, F-10/1, Islamabad"),
    ("Aymen Abid", "House 450, street 6/1, Block D, sector O-9 Police Foundation, Islamabad"),
    ("Fahad Rao", "Apartment 8, Block 2, PHA Apartments, G-8/4, Islamabad"),
    ("Gul Perwasha Cheema", "House #1553, Street #44 Usman Block phase 8 Bahria Town Rawalpindi"),
    ("Hamza Shahid", "House 141 Lane 2 Green Villas Adyala Road Rawalpindi"),
    ("Haroon Ali", "House# 221, Street 33, F-10/1, Islamabad"),
    ("Haroon Yasin", "House# 221, Street 33, F-10/1, Islamabad"),
    ("Hassan Shahzad", "2nd Floor Apartment No S2 55 Tower D-Markaz Gulberg Greens, Islamabad"),
    ("Hataf Bin Atif", "Block DD, PWD Housing Society Islamabad"),
    ("Iffat Maab Akhtar", "House#986 I, St #45, Phase 5, Bahria Town Islamabad"),
    ("Iqra Zanib", "I10 Islamabad"),
    ("JAHAN ZAIB", "Jhangi Syedan, Islamabad"),
    ("Jahanzeb Ahmad", "Cb 173/5, St#3, Jinnah Road, Lalazar, Wah"),
    ("Javariya Mufarrakh", "516, 5th Floor, Warda Hamna 1, G11/3, Islamabad"),
    ("Jawwad Ali", "Khasra no 430 Street 15, Lane 10 Park Road Islamabad"),
    ("Laraib Sarfraz", "Satellite Town, Rawalpindi"),
    ("MUHAMMAD OMER MAZHAR RANA", "House 236, street 39, sector G-14/4, Islamabad"),
    ("Mahnoor Tanweer", "DHA 2, Islamabad"),
    ("Mariam Ali Bokhari", "House 32-A, Street 24, F8/2, Islamabad"),
    ("Mashhood Ali Rastgar", "House 32-A, Street 24, F8/2, Islamabad"),
    ("Mavia", "flat 5B, Floor 5th, sudais Tower, khyber super market sadar peshawar"),
    ("Mehwish Bibi", "Sohan Bus Stop ISB"),
    ("Momina Raja", "House 61, 70 Park Avenue S.C.H.S E/11-2 Islamabad"),
    ("Momna Tariq", "House # L-692, Street # 3A, Qasimabad, Rawalpindi"),
    ("Muhammad Danish Iqbal", "Block No: 10-D, Flat No: 7, AGPR Colony, G-9/2, Islamabad"),
    ("Muhammad Hammad Sarfraz", "Street 97, E13, PHA Flats, G11"),
    ("Muhammad Haris", "House 14, Street 36, River Gardens, O-9, Islamabad"),
    ("Muhammad Jalal Khan", "House 78, Street 33-A, Sector I-10/2 Islamabad"),
    ("Muhammad Kamal", "House no 111-B, Street 89 wapda colony, G-7/4 Islamabad"),
    ("Muhammad Kamran Taj", "House 46-F, Street No.4, Sector G-8/2, Islamabad"),
    ("Muhammad Mehdi Abbas", "Bangash Colony, Rawalpindi"),
    ("Muhammad Raees Shujaan Azhar", "House No. 1694, Street No. 79-A, Sector I-10/1, Islamabad"),
    ("Muhammad Saim", "House # 6, phase # 2, Ghauri Town, Islamabad"),
    ("Muhammad Talha", "House No 301 Street 4F Ghauri Town VIP Phase Islamabad"),
    ("Muhammad Umar Raza", "Mollah Lass Near Masjid Billal Main Loh-E-Dandi Rode noor pur Shah Islamabad"),
    ("Muhammad Zain ul Abadin", "House K/504, Zafar ul haq road, Rawalpindi"),
    ("Muhammad Zeeshan Usaid", "H-119, street 4, Phase 4C-1 Ghouri Town Islamabad"),
    ("Muhammad Usman Mughal", "H#10, Street 6, Khokharabad near Chatri Chowk, KRL Road, Rawalpindi"),
    ("Muqadas Saleem", "House no. 27, Main Street, Jan Colony, Chaklala Scheme 3, Rawalpindi"),
    ("Noor Faiz Malik", "House 1183, Street 63, G-10/4, Islamabad"),
    ("Muhammad Usman Javed", "House No. 11, Street-4, CVRP, Emaar DHA, Islamabad"),
    ("Osama Ahmad", "House 723 - J, Street 179, G11/1, Islamabad"),
    ("QURAT UL AIN", "House 102, street 3, Block B, park view city Islamabad"),
    ("Raheela Akhtar", "House No. 451, Street 13, Road A Bahria Town Phase 4"),
    ("Ramisha Riaz Sheikh", "House no. 485, Street no. 52, G-9/1"),
    ("Ramsha Khurshid", "House #02 street 23a sector A1 next to future world school phase 8 bahria town"),
    ("Rida Nayyab", "H#42, St#02, Jan Colony, Chaklala Scheme 3, Rawalpindi"),
    ("Saad Zahid", "F275/S, F-Block, Satellite Town, Rawalpindi"),
    ("Saleh Muhammad", "Galaxy Hostel, Near Shamsabad Merto station, Rawalpindi"),
    ("Salman Iqbal", "House No.i666 Street No.4 teli Muhalah Rwp"),
    ("Sameer Sheikh", "H.No 35, Street 4C, Habib Town, Lawyer's Colony, Gulzar-e-Quaid, Rawalpindi"),
    ("Sohaib Danish", "Street 2, I10/2, Islamabad"),
    ("Summaya Shakur", "DHA 2, El Ceilo A"),
    ("Syed Junaid Ali Zaidi", "House no 254, Awan Street No 4, Mubarik Lane, Adyala Road, Rawalpindi"),
    ("Taloot Ahmad Malik", "House 71 Sector J, DHA 2 Islamabad"),
    ("Tariq Asim", "Zarkon Heights - G/15"),
    ("Tehniat Taqdees Masood", "House no 4, bangash street, car chowk near safari villas Rawalpindi"),
    ("Unsa Umar", "House no 86, Street 159, G-11/1, Islamabad"),
    ("Usman Imtiaz", "House no 03, Qazi Street, Near Qazi Market, New Gulzar-e-Quaid. Rawalpindi"),
    ("Zeest Hassan Qureshi", "House No 95, Street 66, F11/4, Islamabad"),
    ("Zeshan Ali", "Apartment No: 407, 4th Floor, Landmark III, Near to Gate No.6 Nust University, Nust Service Road, H-13, Islamabad"),
    ("Zunaira Shahid", "Sadqabad Rawalpindi"),
]

def extract_sector_code(address):
    """Extract sector code from address."""
    parts = address.upper().split()
    for i, part in enumerate(parts):
        # Look for sector codes like I-9, F-10, G-8, etc.
        if len(part) >= 3 and part[0] in 'EFGHIO' and part[1] == '-':
            return part[:3]  # E.g., "I-9", "F-10"
    return None

def find_coordinates(name, address):
    """Find coordinates using multiple methods."""
    geolocator = Nominatim(user_agent="oreo_exact_coords")

    # Method 1: Try Nominatim first
    try:
        location = geolocator.geocode(f"{address}, Pakistan", timeout=5)
        if location:
            return (round(location.latitude, 6), round(location.longitude, 6), "EXACT")
    except:
        pass

    # Method 2: Check sector code database
    sector = extract_sector_code(address)
    if sector and sector in ISLAMABAD_SECTORS:
        return (ISLAMABAD_SECTORS[sector][0], ISLAMABAD_SECTORS[sector][1], "SECTOR")

    # Method 3: Check for known landmarks
    for landmark, coords in RAWALPINDI_LANDMARKS.items():
        if landmark.lower() in address.lower():
            return (coords[0], coords[1], "LANDMARK")

    # Method 4: Try just the city name
    try:
        if "Lahore" in address:
            location = geolocator.geocode("Lahore, Pakistan", timeout=5)
            if location:
                return (round(location.latitude, 6), round(location.longitude, 6), "CITY")
    except:
        pass

    return (None, None, "NOT_FOUND")

def extract_all_coordinates():
    """Extract coordinates for all employees."""
    print("[EXTRACTING EXACT COORDINATES FOR 67 EMPLOYEES]")
    print("-" * 80)

    results = []
    exact_count = 0
    sector_count = 0
    landmark_count = 0
    notfound_count = 0

    for idx, (name, address) in enumerate(EMPLOYEES, 1):
        lat, lon, method = find_coordinates(name, address)

        if method == "EXACT":
            exact_count += 1
            status = "EXACT"
        elif method == "SECTOR":
            sector_count += 1
            status = "SECTOR_CENTER"
        elif method == "LANDMARK":
            landmark_count += 1
            status = "LANDMARK"
        elif method == "CITY":
            status = "CITY_CENTER"
        else:
            notfound_count += 1
            status = "NEEDS_MANUAL"
            lat, lon = "MANUAL", "MANUAL"

        coord_str = f"{lat}, {lon}" if lat != "MANUAL" else "PENDING MANUAL LOOKUP"

        results.append({
            "Name": name,
            "Address": address,
            "Latitude": lat,
            "Longitude": lon,
            "Google_Coordinates": coord_str,
            "Method": status
        })

        print(f"[{idx}/67] {name:30} | {status:15} | {coord_str}")
        time.sleep(0.1)

    # Save results
    output_file = "output/exact_coordinates_for_sheet.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Address", "Latitude", "Longitude", "Google_Coordinates", "Method"])
        writer.writeheader()
        writer.writerows(results)

    print("-" * 80)
    print(f"\n[RESULTS SUMMARY]")
    print(f"  EXACT coordinates found:      {exact_count}")
    print(f"  Sector center coordinates:    {sector_count}")
    print(f"  Landmark-based coordinates:   {landmark_count}")
    print(f"  Needs manual verification:    {notfound_count}")
    print(f"  TOTAL:                        {len(EMPLOYEES)}")
    print(f"\n[OUTPUT FILE] {output_file}")
    print(f"\n[NEXT STEP] Copy 'Google_Coordinates' column to your Google Sheet")

if __name__ == "__main__":
    extract_all_coordinates()
