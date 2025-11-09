#!/usr/bin/env python3
"""
Railway Fresh Setup - Tamamen yeni process
"""

import os
import sys

# Environment variables - YENİ Railway bilgileri
os.environ['DATABASE_URL'] = 'postgresql://postgres:kJQQiRoGKGgWRPWGsRrSdKRoMogEVAGy@shinkansen.proxy.rlwy.net:27699/railway'
os.environ['DB_TYPE'] = 'postgresql'
os.environ['FLASK_ENV'] = 'production'

print("=" * 60)
print("🚀 RAILWAY FRESH SETUP")
print("=" * 60)
print()

# Import sonrası
from sqlalchemy import create_engine, text, inspect

engine = create_engine(os.environ['DATABASE_URL'].replace('postgresql://', 'postgresql+psycopg2://'))

print("📡 Railway'e bağlanılıyor...")

with engine.connect() as conn:
    # Schema'yı temizle
    print("🗑️  Schema temizleniyor...")
    conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
    conn.execute(text("CREATE SCHEMA public"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
    conn.commit()
    print("✅ Schema temizlendi")

print()
print("📊 Flask app ile tabloları oluşturuluyor...")

# Şimdi Flask app'i import et
from app import app, db

with app.app_context():
    # Tabloları oluştur (index hatalarını ignore et)
    try:
        db.create_all()
    except Exception as e:
        error_msg = str(e).lower()
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            print(f"⚠️  Index hatası ignore edildi")
        else:
            print(f"\n❌ Hata: {str(e)[:200]}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Kontrol et
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\n✅ {len(tables)} tablo oluşturuldu:")
    for table in sorted(tables):
        print(f"   ✓ {table}")
    
    print()
    print("=" * 60)
    print("🎉 SETUP BAŞARILI!")
    print("=" * 60)
