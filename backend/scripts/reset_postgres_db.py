#!/usr/bin/env python3
"""
Reset PostgreSQL Database
Drops and recreates the system_rebellion database to fix auth issues after SQLite migration.
"""
import sys
import subprocess
import os
from pathlib import Path

# Database configuration
DB_NAME = "system_rebellion"
DB_USER = "rebellion_user"
DB_PASSWORD = "ChangeThisPassword123!"
DB_HOST = "localhost"
DB_PORT = "5432"

def run_psql_command(command: str, db_name: str = "postgres") -> tuple[int, str, str]:
    """Run a psql command and return the result."""
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    
    cmd = [
        'psql',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', db_name,
        '-c', command
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result.returncode, result.stdout, result.stderr

def drop_database():
    """Drop the database if it exists."""
    print(f"🗑️  Dropping database '{DB_NAME}'...")
    
    # First, terminate all connections to the database
    terminate_cmd = f"""
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '{DB_NAME}'
    AND pid <> pg_backend_pid();
    """
    
    returncode, stdout, stderr = run_psql_command(terminate_cmd, "postgres")
    if returncode != 0 and "does not exist" not in stderr:
        print(f"⚠️  Warning terminating connections: {stderr}")
    else:
        print("   ✅ Terminated existing connections")
    
    # Now drop the database
    drop_cmd = f"DROP DATABASE IF EXISTS {DB_NAME};"
    returncode, stdout, stderr = run_psql_command(drop_cmd, "postgres")
    
    if returncode != 0:
        print(f"   ❌ Error dropping database: {stderr}")
        return False
    
    print(f"   ✅ Database '{DB_NAME}' dropped successfully")
    return True

def create_database():
    """Create a fresh database."""
    print(f"🏗️  Creating database '{DB_NAME}'...")
    
    create_cmd = f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};"
    returncode, stdout, stderr = run_psql_command(create_cmd, "postgres")
    
    if returncode != 0:
        print(f"   ❌ Error creating database: {stderr}")
        return False
    
    print(f"   ✅ Database '{DB_NAME}' created successfully")
    return True

def run_alembic_migrations():
    """Run Alembic migrations to set up the schema."""
    print("🔄 Running Alembic migrations...")
    
    backend_dir = Path(__file__).parent
    
    # First, ensure alembic is at the head
    result = subprocess.run(
        ['alembic', 'upgrade', 'head'],
        cwd=backend_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"   ❌ Error running migrations: {result.stderr}")
        return False
    
    print("   ✅ Migrations completed successfully")
    print(result.stdout)
    return True

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  System Rebellion - PostgreSQL Database Reset             ║
║  🧐 Sir Hawkington supervises the database reset          ║
║  🐌 Meth Snail optimizes the process                      ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print(f"\n⚠️  WARNING: This will DROP and RECREATE the database '{DB_NAME}'")
    print("   All existing data will be PERMANENTLY DELETED!\n")
    print(f"   Database: {DB_NAME}")
    print(f"   Host: {DB_HOST}:{DB_PORT}")
    print(f"   User: {DB_USER}\n")
    
    response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Database reset cancelled")
        sys.exit(0)
    
    print("\n" + "="*60)
    
    # Step 1: Drop database
    if not drop_database():
        print("\n❌ Failed to drop database")
        sys.exit(1)
    
    # Step 2: Create database
    if not create_database():
        print("\n❌ Failed to create database")
        sys.exit(1)
    
    # Step 3: Run migrations
    if not run_alembic_migrations():
        print("\n❌ Failed to run migrations")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("\n🎉 Database reset complete!")
    print("\n✅ Next steps:")
    print("   1. Start your backend server")
    print("   2. Test user registration and login")
    print("   3. Verify all auth endpoints are working\n")

if __name__ == "__main__":
    main()
