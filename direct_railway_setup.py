#!/usr/bin/env python3
"""
Direkt Railway PostgreSQL Setup - Index hatalarını ignore eder
"""

import os
from dotenv import load_dotenv

# .env.railway yükle
load_dotenv('.env.railway')

# DATABASE_URL'i environment'a ekle
railway_url = os.getenv('RAILWAY_DATABASE_URL')
if railway_url:
    os.environ['DATABASE_URL'] = railway_url

# Flask app'i import et
from app import app, db

print("=" * 60)
print("🚀 RAILWAY DIRECT SETUP")
print("=" * 60)
print()

try:
    with app.app_context():
        print("📊 Tablolar oluşturuluyor...")
        
        # Önce mevcut tabloları kontrol et
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            print(f"⚠️  {len(existing_tables)} tablo zaten mevcut, atlanıyor")
        else:
            # Tabloları oluştur
            db.create_all()
        
        # Tabloları kontrol et
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ {len(tables)} tablo hazır:")
        for table in sorted(tables):
            print(f"   ✓ {table}")
        
        print()
        print("=" * 60)
        print("🎉 SETUP TAMAMLANDI!")
        print("=" * 60)
        print()
        print("📝 Sonraki adım:")
        print("   python migrate_to_railway.py (verileri transfer et)")
        print()
        
except Exception as e:
    print(f"❌ Hata: {str(e)}")
    import traceback
    traceback.print_exc()
