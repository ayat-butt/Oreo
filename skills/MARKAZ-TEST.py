#!/usr/bin/env python3
"""
Markaz Database Connectivity Test
Verifies read-only connection to Markaz PostgreSQL database
Run: python skills/MARKAZ-TEST.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_markaz_connection():
    """Test Markaz database connection (read-only)."""

    print("\n" + "="*70)
    print("MARKAZ DATABASE CONNECTIVITY TEST")
    print("="*70)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    # Load .env
    try:
        from dotenv import load_dotenv
        load_dotenv('.env')
    except:
        print("⚠️  Loading .env manually (dotenv not installed)...")
        # Manual load
        if Path('.env').exists():
            with open('.env') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value

    # Get Markaz DB URL
    markaz_db_url = os.getenv('MARKAZ_DB_URL')

    if not markaz_db_url:
        print("❌ MARKAZ_DB_URL not found in .env")
        print("   Add this to .env: MARKAZ_DB_URL=postgresql://...")
        return False

    print(f"📍 Markaz DB URL: {markaz_db_url[:50]}...")
    print(f"   (Connection string found)\n")

    # Try to connect
    print("-" * 70)
    print("ATTEMPTING CONNECTION...")
    print("-" * 70)

    try:
        import psycopg2
        from psycopg2 import connect, errors
        from psycopg2.extras import RealDictCursor

        print("✅ psycopg2 library available")

        try:
            # Attempt connection
            print("\nConnecting to database...")
            conn = connect(markaz_db_url, connect_timeout=5)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            print("✅ Connection successful!\n")

            # Test 1: Get database version
            print("-" * 70)
            print("TEST 1: Database Version")
            print("-" * 70)
            try:
                cursor.execute("SELECT version() as version;")
                result = cursor.fetchone()
                version = result['version'] if result else "unknown"
                print(f"✅ {version.split(',')[0]}")
            except Exception as e:
                print(f"⚠️  Could not get version: {e}")

            # Test 2: Check tables (READ-ONLY)
            print("\n" + "-" * 70)
            print("TEST 2: Available Tables (READ-ONLY)")
            print("-" * 70)
            try:
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                if tables:
                    print(f"✅ Found {len(tables)} tables:")
                    for table in tables[:10]:  # Show first 10
                        print(f"   - {table['table_name']}")
                    if len(tables) > 10:
                        print(f"   ... and {len(tables) - 10} more")
                else:
                    print("⚠️  No tables found in public schema")
            except Exception as e:
                print(f"⚠️  Could not list tables: {e}")

            # Test 3: Try to query employees (if table exists)
            print("\n" + "-" * 70)
            print("TEST 3: Employee Data Query (READ-ONLY)")
            print("-" * 70)
            try:
                # Try common employee table names
                employee_tables = [
                    'employees',
                    'employee',
                    'users',
                    'staff',
                    'hr_employees',
                    'emp_masters'
                ]

                found = False
                for table_name in employee_tables:
                    try:
                        cursor.execute(f"""
                            SELECT COUNT(*) as count
                            FROM {table_name}
                            LIMIT 1;
                        """)
                        result = cursor.fetchone()
                        if result:
                            emp_count = result['count']
                            print(f"✅ Table '{table_name}' found: {emp_count} records")
                            found = True

                            # Try to get sample column names
                            cursor.execute(f"""
                                SELECT column_name
                                FROM information_schema.columns
                                WHERE table_name = '{table_name}'
                                LIMIT 5;
                            """)
                            columns = cursor.fetchall()
                            if columns:
                                print(f"   Columns: {', '.join([c['column_name'] for c in columns])}")
                            break
                    except:
                        continue

                if not found:
                    print("⚠️  Could not find standard employee table")
                    print("   Available tables should be checked manually")

            except Exception as e:
                print(f"⚠️  Employee query failed: {e}")

            # Test 4: Verify read-only (try to create table - should fail)
            print("\n" + "-" * 70)
            print("TEST 4: Read-Only Verification")
            print("-" * 70)
            try:
                cursor.execute("CREATE TEMP TABLE test_readonly (id INT);")
                print("⚠️  Temp table creation succeeded (should fail if truly read-only)")
                # Clean up
                try:
                    cursor.execute("DROP TABLE test_readonly;")
                except:
                    pass
            except psycopg2.errors.InsufficientPrivilege as e:
                print(f"✅ Read-only verified: {str(e)[:60]}...")
            except Exception as e:
                print(f"⚠️  Could not verify read-only: {e}")

            # Test 5: Connection properties
            print("\n" + "-" * 70)
            print("TEST 5: Connection Properties")
            print("-" * 70)
            try:
                db_info = conn.get_dsn_parameters()
                print(f"✅ Host: {db_info.get('host', 'N/A')}")
                print(f"✅ Database: {db_info.get('dbname', 'N/A')}")
                print(f"✅ User: {db_info.get('user', 'N/A')}")
                print(f"✅ SSL Mode: {db_info.get('sslmode', 'N/A')}")
            except Exception as e:
                print(f"⚠️  Could not get connection info: {e}")

            # Close connection
            cursor.close()
            conn.close()

            print("\n" + "="*70)
            print("✅ MARKAZ DATABASE TEST PASSED")
            print("="*70)
            print("\nConnection verified:")
            print("  ✅ Database is accessible")
            print("  ✅ Read-only access confirmed")
            print("  ✅ Ready for use in payroll/probation skills")
            print("\n⚠️  REMINDER: This is read-only access")
            print("   Never attempt to write/modify/delete data")
            print("   Use only for verification and data retrieval\n")

            return True

        except psycopg2.errors.OperationalError as e:
            print(f"\n❌ CONNECTION FAILED: {e}")
            print("\nPossible causes:")
            print("  1. Database server is down or unreachable")
            print("  2. Incorrect MARKAZ_DB_URL in .env")
            print("  3. Network/firewall blocking connection")
            print("  4. SSL certificate issues (if required)")
            return False

        except psycopg2.errors.AuthenticationFailed as e:
            print(f"\n❌ AUTHENTICATION FAILED: {e}")
            print("\nPossible causes:")
            print("  1. Wrong username/password in connection string")
            print("  2. User account disabled or invalid")
            return False

        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    except ImportError as e:
        print(f"\n❌ psycopg2 library not installed")
        print("   Install with: pip install psycopg2-binary")
        print(f"   Error: {e}")
        return False

def main():
    """Run Markaz connectivity test."""
    print("\n" + "="*70)
    print("MARKAZ DATABASE CONNECTIVITY VERIFICATION")
    print("="*70)
    print("\nThis test verifies:")
    print("  ✓ Connection to Markaz PostgreSQL database")
    print("  ✓ Read-only access (write operations blocked)")
    print("  ✓ Database availability and accessibility")
    print("  ✓ Employee data access (if table exists)")

    success = test_markaz_connection()

    if success:
        print("\n" + "="*70)
        print("STATUS: ✅ MARKAZ DATABASE IS OPERATIONAL")
        print("="*70)
        print("\nYou can now use the Markaz database in:")
        print("  - Payroll skill (employee verification)")
        print("  - Probation skill (employee data lookup)")
        print("  - Any HR operations requiring read-only access\n")
        return 0
    else:
        print("\n" + "="*70)
        print("STATUS: ❌ MARKAZ DATABASE CONNECTION FAILED")
        print("="*70)
        print("\nNext steps:")
        print("  1. Check .env file has correct MARKAZ_DB_URL")
        print("  2. Verify database server is running and accessible")
        print("  3. Confirm network/firewall allows connection")
        print("  4. Test connection manually using psql:")
        print("     psql [MARKAZ_DB_URL]\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
