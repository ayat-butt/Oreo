#!/usr/bin/env python3
"""
Geocode employee addresses from the carpooling list.
Converts postal addresses to GPS coordinates (latitude, longitude).
Outputs results to CSV for import into Google Maps.
"""

import csv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

# Employee data from the spreadsheet
EMPLOYEES = [
    ("Abdul Rehman", "Bahria Boys Hostel Near Sawan Taxi Stand, Islamabad"),
    ("Abdul Rehman Siddiqi", "House 630, St 2, I-9/1 Islamabad"),
    ("Abdur Rehman", "Alipur Islamabad"),
    ("Ahmed Javed", "65-Lytton road, Lahore"),
    ("Ahsan Javed", "Near National Model School Village Bikhari kalan Tehsil & District Chakwal"),
    ("Amena Ahmed", "House # 134, Street 37, F-10/1, Islamabad"),
    ("Aymen Abid", "House 450, street 6/1, Block D, sector O-9 Police Foundation, Islamabad, Pakistan"),
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

def geocode_addresses():
    """Geocode all employee addresses and save to CSV."""

    # Initialize geocoder
    geolocator = Nominatim(user_agent="oreo_carpooling_geocoder")

    results = []
    successful = 0
    failed = 0

    print(f"[GEOCODING] Processing {len(EMPLOYEES)} employee addresses...")
    print("-" * 80)

    for idx, (name, address) in enumerate(EMPLOYEES, 1):
        try:
            # Add Pakistan context for better accuracy
            full_address = f"{address}, Pakistan"

            print(f"[{idx}/{len(EMPLOYEES)}] Geocoding {name}...", end=" ")

            # Geocode the address
            location = geolocator.geocode(full_address, timeout=10)

            if location:
                results.append({
                    "Name": name,
                    "Address": address,
                    "Latitude": round(location.latitude, 6),
                    "Longitude": round(location.longitude, 6),
                    "Maps_URL": f"https://maps.google.com/?q={location.latitude},{location.longitude}",
                    "Status": "FOUND"
                })
                print(f"FOUND")
                successful += 1
            else:
                results.append({
                    "Name": name,
                    "Address": address,
                    "Latitude": "N/A",
                    "Longitude": "N/A",
                    "Maps_URL": "",
                    "Status": "NOT_FOUND"
                })
                print(f"NOT_FOUND")
                failed += 1

            # Rate limiting to avoid overloading the service
            time.sleep(0.5)

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"ERROR: {str(e)[:30]}")
            results.append({
                "Name": name,
                "Address": address,
                "Latitude": "N/A",
                "Longitude": "N/A",
                "Maps_URL": "",
                "Status": f"ERROR"
            })
            failed += 1
            time.sleep(1)

    # Save results to CSV
    output_file = "output/employee_coordinates.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Address", "Latitude", "Longitude", "Maps_URL", "Status"])
        writer.writeheader()
        writer.writerows(results)

    print("-" * 80)
    print(f"\n[RESULTS]")
    print(f"  Successfully geocoded: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(EMPLOYEES)}")
    print(f"\n[OUTPUT] Saved to: {output_file}")
    print(f"\n[NEXT STEPS]")
    print(f"  1. Review the CSV file")
    print(f"  2. Import coordinates into Google Maps")
    print(f"  3. Use for carpooling route optimization")

if __name__ == "__main__":
    geocode_addresses()
