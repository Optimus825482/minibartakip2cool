"""
Migration: Add kritik_stok_seviyesi to PersonelZimmetDetay

Bu migration, PersonelZimmetDetay tablosuna kritik_stok_seviyesi alanını ekler.
Kat sorumluları bu alan ile her zimmet detayı için kendi kritik seviyelerini belirleyebilirler.

Kullanım:
    python migrations/add_kritik_seviye_to_zimmet_detay.py

Revision ID: 001
Create Date: 2025-01-05
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from models import db
from app import app

def upgrade():
    """Add kritik_stok_seviyesi column to personel_zimmet_detay table"""
    try:
        with app.app_context():
            # Check if column already exists
            result = db.session.execute(text(
                "SELECT COUNT(*) FROM pragma_table_info('personel_zimmet_detay') "
                "WHERE name='kritik_stok_seviyesi'"
            ))
            exists = result.scalar() > 0
            
            if exists:
                print("✓ Column 'kritik_stok_seviyesi' already exists. Skipping migration.")
                return True
            
            # Add the column
            db.session.execute(text(
                "ALTER TABLE personel_zimmet_detay "
                "ADD COLUMN kritik_stok_seviyesi INTEGER"
            ))
            db.session.commit()
            
            print("✓ Successfully added 'kritik_stok_seviyesi' column to personel_zimmet_detay table")
            return True
            
    except Exception as e:
        db.session.rollback()
        print(f"✗ Migration failed: {str(e)}")
        return False

def downgrade():
    """Remove kritik_stok_seviyesi column from personel_zimmet_detay table"""
    try:
        with app.app_context():
            # SQLite doesn't support DROP COLUMN directly
            # We need to recreate the table without the column
            print("⚠ Downgrade not implemented for SQLite.")
            print("  To remove the column, you need to recreate the table manually.")
            return False
            
    except Exception as e:
        print(f"✗ Downgrade failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("Starting migration: Add kritik_stok_seviyesi to PersonelZimmetDetay")
    print("-" * 70)
    
    success = upgrade()
    
    if success:
        print("-" * 70)
        print("✓ Migration completed successfully!")
    else:
        print("-" * 70)
        print("✗ Migration failed!")
        exit(1)
