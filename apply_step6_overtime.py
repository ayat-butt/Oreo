#!/usr/bin/env python3
"""
STEP 6: Apply Overtime Approvals to payroll
Add all 23 approved overtime entries from Markaz
"""

import json
import psycopg2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('=' * 80)
print('STEP 6: APPLYING OVERTIME APPROVALS')
print('=' * 80)
print()

# Fetch overtime data from Markaz
DB_URL = os.getenv('MARKAZ_DB_URL')
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

query = """
SELECT
    CONCAT(u.first_name, ' ', u.last_name) as full_name,
    u.email,
    ot.total_hours,
    ot.calculated_amount,
    ot.status,
    ot.hr_status
FROM overtime_requests ot
JOIN users u ON ot.user_id = u.id
WHERE ot.hr_status = 'moved_to_april_2026_payroll'
AND ot.status = 'approved'
ORDER BY u.first_name, u.last_name
"""

cursor.execute(query)
overtime_records = cursor.fetchall()

print(f'Found {len(overtime_records)} approved overtime entries from Markaz')
print()

overtime_data = {}
for record in overtime_records:
    name, email, hours, amount, status, hr_status = record
    overtime_data[name.strip()] = float(amount) if amount else 0

# Apply to payroll
metadata = service.spreadsheets().get(spreadsheetId=PAYROLL_SHEET_ID).execute()
sheets = [sheet['properties']['title'] for sheet in metadata['sheets']]

applied = 0
not_found = []

for entity in sheets:
    result = service.spreadsheets().values().get(
        spreadsheetId=PAYROLL_SHEET_ID,
        range=f'{entity}!A1:M500'
    ).execute()

    values = result.get('values', [])

    for row_idx, row in enumerate(values):
        if row_idx == 0:
            continue
        if len(row) < 2:
            continue

        emp_name = str(row[1]).strip() if len(row) > 1 else ''

        for ot_name, ot_amount in overtime_data.items():
            if ot_name.lower() == emp_name.lower():
                # Column M = Overtime (column 12)
                service.spreadsheets().values().update(
                    spreadsheetId=PAYROLL_SHEET_ID,
                    range=f'{entity}!M{row_idx + 1}',
                    valueInputOption='RAW',
                    body={'values': [[ot_amount]]}
                ).execute()
                applied += 1
                print(f'Applied PKR {ot_amount:,.0f} overtime to {emp_name} in {entity}')
                break

if applied < len(overtime_records):
    not_found = [name for name in overtime_data.keys() if name not in ' '.join([row[1] if len(row) > 1 else '' for entity in sheets for row in values])]

cursor.close()
conn.close()

print()
print('=' * 80)
print('STEP 6 COMPLETE')
print('=' * 80)
print(f'Applied: {applied} out of {len(overtime_records)} overtime entries')
