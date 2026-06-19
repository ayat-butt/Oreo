#!/usr/bin/env python3
"""Check employee by CNIC."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

def main():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cnic = '6110198676046'

    # Search by CNIC
    cur.execute("""
        SELECT
            user_id,
            cnic_number,
            compensation_status,
            joining_date
        FROM employee_profiles
        WHERE cnic_number = %s
    """, (cnic,))

    result = cur.fetchone()
    conn.close()

    if result:
        print(f"\nFound employee by CNIC {cnic}:\n")
        print(f"Name: {result['user_id']}")
        print(f"CNIC: {result['cnic_number']}")
        print(f"Compensation Status: '{result['compensation_status']}'")
        print(f"Joining Date: {result['joining_date']}")
    else:
        print(f"\nNo employee found with CNIC: {cnic}")

if __name__ == "__main__":
    main()
