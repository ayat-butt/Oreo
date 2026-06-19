#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ANNUAL TAX ANALYSIS (FY Jul 2025 - Jun 2026)
Analyze previous payroll sheets to understand tax pattern
Extract and track income tax deductions month by month
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

# Previous payroll sheet IDs (Jul 2025 - Mar 2026)
payroll_sheets = {
    'July 2025': {
        'id': '1j9IYtxj38mUYPT8kOGOhuyOm7wtbiccaCjxJPTvlM24',
        'gid': '465044693'
    },
    'August 2025': {
        'id': '1FCiMTGim6EqWJRL7UVA3V31bH8KvICVs7a895pjoIuE',
        'gid': '582912202'
    },
    'September 2025': {
        'id': '1sLo1cv5tWqoj1Shtyp2eZjSW6UEz_z__VU8CnFDfW-A',
        'gid': '582912202'
    },
    'October 2025': {
        'id': '1nCuye_IqKEipyKNWvAz9pJ3LLwEpnR2z6raoPVfmGRY',
        'gid': 'PRIMARY'
    },
    'November 2025': {
        'id': '1NHnjvsJc-hk9l7qQvOTQr3znKFPzjc9mEBbtKWmJjjA',
        'gid': 'PRIMARY'
    },
    'December 2025': {
        'id': '1FprPYHx-S_RaV-C5HGGENg3BVeWzhmn3eUx1Ofuk7gk',
        'gid': 'PRIMARY'
    },
    'January 2026': {
        'id': '1EXJhbbqI952ick9-VhSX3k6MxC6oGSVeg9NJfrlYqeI',
        'gid': '1791900528'
    },
    'February 2026': {
        'id': '1v-vLLvij1phN_havWvGzbOWaz1apQcs3unHAectyTdY',
        'gid': '1791900528'
    },
    'March 2026': {
        'id': '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk',
        'gid': 'PRIMARY'
    }
}

print('=' * 120)
print('ANALYZING ANNUAL TAX PATTERN (FY Jul 2025 - Jun 2026)')
print('=' * 120)
print()

print('Loading payroll sheets to extract tax data...')
print('-' * 120)
print()

# Try to load and analyze each sheet
monthly_tax_data = {}

for month, sheet_info in payroll_sheets.items():
    print(f'{month}:')
    print(f'  Sheet ID: {sheet_info["id"][:20]}...')

    try:
        # Try to get sheet metadata first to find the correct range
        metadata = service.spreadsheets().get(
            spreadsheetId=sheet_info['id']
        ).execute()

        sheet_titles = [s['properties']['title'] for s in metadata['sheets']]
        print(f'  Available tabs: {", ".join(sheet_titles[:3])}...')

        # Try to load from first tab (usually has entity-wise data)
        # For now, just record that we need to read it
        monthly_tax_data[month] = {
            'sheet_id': sheet_info['id'],
            'status': 'TO_READ'
        }

        print(f'  Status: Ready to load')
        print()

    except Exception as e:
        print(f'  Error: {str(e)[:60]}...')
        print()

print('=' * 120)
print('NEXT STEP')
print('=' * 120)
print()
print('To properly analyze the tax pattern, I need to:')
print()
print('1. Load each month\'s payroll sheet (Jul 2025 - Mar 2026)')
print('2. Extract "Income Tax" column for each employee')
print('3. Build a 9-month tax history per employee')
print('4. Calculate total tax deducted so far')
print('5. Determine annual gross salary estimate')
print('6. Calculate remaining tax for Apr-May-Jun 2026')
print('7. Apply April 2026 tax based on financial year calculation')
print()
print('Ready to proceed. Please confirm you have access to all sheets.')
print()
