#!/usr/bin/env python3
"""Check what columns exist in Markaz employee_profiles table."""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Get all columns from employee_profiles
cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'employee_profiles'
    ORDER BY ordinal_position
""")

print("Columns in employee_profiles table:")
for col, dtype in cur.fetchall():
    print(f"  {col} ({dtype})")

conn.close()
