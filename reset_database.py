"""
Reset PostgreSQL database
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to PostgreSQL server
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'minibar_user'),
        password=os.getenv('DB_PASSWORD', 'minibar123'),
        port=int(os.getenv('DB_PORT', 5433)),
        database='postgres'  # Connect to default database
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    db_name = os.getenv('DB_NAME', 'minibar_takip')
    
    # Terminate existing connections
    cursor.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_name}'
        AND pid <> pg_backend_pid()
    """)
    
    # Drop database if exists
    cursor.execute(f'DROP DATABASE IF EXISTS {db_name}')
    print(f"✅ Database '{db_name}' dropped")
    
    # Create database
    cursor.execute(f'CREATE DATABASE {db_name}')
    print(f"✅ Database '{db_name}' created successfully!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
