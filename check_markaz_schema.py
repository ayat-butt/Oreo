#!/usr/bin/env python3
"""
Check Markaz database schema to find overtime table structure
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('MARKAZ_DB_URL')

try:
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    print('=' * 80)
    print('MARKAZ DATABASE SCHEMA')
    print('=' * 80)
    print()

    # Get all tables
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)

    tables = cursor.fetchall()
    print('TABLES IN DATABASE:')
    for table in tables:
        print(f'  - {table[0]}')

    print()
    print('-' * 80)
    print()

    # Look for overtime-related tables
    overtime_tables = [t[0] for t in tables if 'overtime' in t[0].lower()]

    if overtime_tables:
        for table_name in overtime_tables:
            print(f'TABLE: {table_name}')
            print('COLUMNS:')
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f'  - {col[0]} ({col[1]})')
            print()

    cursor.close()
    conn.close()

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
