#!/usr/bin/env python3
"""Find where employee names are stored in the database."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)

print("\n" + "=" * 100)
print("SEARCHING FOR EMPLOYEE NAME FIELDS")
print("=" * 100)

# Check all columns in employee_profiles
print("\nAll columns in employee_profiles table:")
cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'employee_profiles'
    ORDER BY column_name
""")

columns = cur.fetchall()
for col in columns:
    print(f"  - {col['column_name']} ({col['data_type']})")

# Check if there's a users table
print("\n\nLooking for users/people/staff tables...")
cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND (table_name LIKE '%user%' OR table_name LIKE '%person%' OR table_name LIKE '%staff%' OR table_name LIKE '%employee%' OR table_name LIKE '%contact%')
    ORDER BY table_name
""")

tables = cur.fetchall()
print("Related tables found:")
for table in tables:
    print(f"  - {table['table_name']}")

# Try to find name field by looking at actual data
print("\n\nChecking actual employee_profiles data for potential name fields...")
cur.execute("""
    SELECT
        id,
        user_id,
        employee_id,
        official_email,
        contact_number,
        father_husband_name
    FROM employee_profiles
    WHERE employee_id IS NOT NULL
    LIMIT 3
""")

samples = cur.fetchall()
print("\nSample records:")
for sample in samples:
    for key, value in sample.items():
        print(f"  {key}: {value}")
    print()

# Check if there's a relationship between employee_profiles and users
print("\nChecking columns with 'name' in them...")
cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'employee_profiles'
    AND column_name ILIKE '%name%'
    ORDER BY column_name
""")

name_cols = cur.fetchall()
if name_cols:
    print("Name-related columns:")
    for col in name_cols:
        print(f"  - {col['column_name']} ({col['data_type']})")
else:
    print("No columns with 'name' in employee_profiles")

# Check users table if it exists
print("\n\nChecking 'users' table if it exists...")
try:
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'users'
        ORDER BY column_name
        LIMIT 20
    """)

    user_cols = cur.fetchall()
    if user_cols:
        print("Users table columns:")
        for col in user_cols:
            print(f"  - {col['column_name']} ({col['data_type']})")

        # Try to get a sample
        cur.execute("SELECT * FROM users LIMIT 1")
        sample = cur.fetchone()
        if sample:
            print("\nSample user record:")
            for key, value in sample.items():
                if value:
                    print(f"  {key}: {value}")
except:
    print("Users table not found or error occurred")

conn.close()
