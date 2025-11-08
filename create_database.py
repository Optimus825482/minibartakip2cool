"""
Create PostgreSQL database
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL server
try:
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='',
        port=5432
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='minibar_takip'")
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute('CREATE DATABASE minibar_takip')
        print("✅ Database 'minibar_takip' created successfully!")
    else:
        print("ℹ️  Database 'minibar_takip' already exists")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nℹ️  Make sure PostgreSQL is running and accessible")
