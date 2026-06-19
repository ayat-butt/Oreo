#!/usr/bin/env python3
"""Check Markaz users table structure to find correct Employee ID field"""

import psycopg2
import os

env = {}
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line:
                key, val = line.split('=', 1)
                env[key] = val

conn = psycopg2.connect(
    host=env.get('MARKAZ_HOST'),
    port=int(env.get('MARKAZ_PORT', 5432)),
    database=env.get('MARKAZ_DB'),
    user=env.get('MARKAZ_USER'),
    password=env.get('MARKAZ_PASSWORD')
)

cur = conn.cursor()

# Check users table structure
cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'users'
    ORDER BY ordinal_position
""")

print("Users table structure:")
print("-" * 60)
for col_name, col_type in cur.fetchall():
    print(f"  {col_name:30} {col_type}")

print("\n" + "=" * 60)
print("\nSample users with all ID fields:")
print("-" * 60)

# Get a few sample users to see all ID fields
cur.execute("""
    SELECT id, first_name, last_name, employee_id, user_code
    FROM users
    LIMIT 5
""")

for row in cur.fetchall():
    print(f"  UUID: {row[0]}")
    print(f"  Name: {row[1]} {row[2]}")
    print(f"  employee_id: {row[3]}")
    print(f"  user_code: {row[4]}")
    print()

conn.close()
