#!/usr/bin/env python3
"""
Fetch overtime approvals from Markaz with HR Status = 'Moved to April 2026 Payroll'
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Markaz database connection
DB_URL = os.getenv('MARKAZ_DB_URL')

print('=' * 80)
print('MARKAZ OVERTIME APPROVALS - APRIL 2026')
print('=' * 80)
print()

try:
    # Connect to database
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    print('Connected to Markaz database...')
    print()

    # Query overtime requests with HR Status = "Moved to April 2026 Payroll"
    query = """
    SELECT
        CONCAT(u.first_name, ' ', u.last_name) as full_name,
        u.email,
        ot.total_hours,
        ot.calculated_amount,
        ot.status,
        ot.hr_status,
        ot.overtime_from,
        ot.overtime_to,
        ot.reason
    FROM overtime_requests ot
    JOIN users u ON ot.user_id = u.id
    WHERE ot.hr_status = 'moved_to_april_2026_payroll'
    AND ot.status = 'approved'
    ORDER BY u.first_name, u.last_name
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print(f'Found {len(results)} overtime approvals for April 2026')
    print()
    print('-' * 80)

    if results:
        for i, row in enumerate(results, 1):
            emp_name, email, hours, amount, status, hr_status, from_date, to_date, reason = row
            print(f'{i}. {emp_name}')
            print(f'   Email: {email}')
            print(f'   Hours: {hours}')
            print(f'   Amount: PKR {amount}')
            print(f'   Status: {status}')
            print(f'   HR Status: {hr_status}')
            print(f'   Period: {from_date} to {to_date}')
            print(f'   Reason: {reason}')
            print()
    else:
        print('No approved overtime requests found for April 2026')

    print('=' * 80)

    cursor.close()
    conn.close()

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
