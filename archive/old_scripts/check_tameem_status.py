#!/usr/bin/env python3
"""Check Tameem's status in Markaz database."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

def main():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Search for Tameem
    cur.execute("""
        SELECT
            user_id,
            cnic_number,
            compensation_status,
            joining_date
        FROM employee_profiles
        WHERE LOWER(user_id) LIKE '%tameem%'
    """)

    results = cur.fetchall()
    conn.close()

    print(f"\nFound {len(results)} record(s) for 'Tameem':\n")

    if results:
        for row in results:
            print(f"Name: {row['user_id']}")
            print(f"CNIC: {row['cnic_number']}")
            print(f"Compensation Status: '{row['compensation_status']}'")
            print(f"Joining Date: {row['joining_date']}")
            print("-" * 60)
    else:
        print("No results found")

if __name__ == "__main__":
    main()
