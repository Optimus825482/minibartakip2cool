#!/usr/bin/env python3
"""
Railway PostgreSQL - FORCE CLEAN (Tüm index'leri sil)
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv('.env.railway')

railway_url = os.getenv('RAILWAY_DATABASE_URL')
if railway_url:
    railway_url = railway_url.replace('postgresql://', 'postgresql+psycopg2://')

engine = create_engine(railway_url)

print("=" * 60)
print("🧹 RAILWAY FORCE CLEAN - TÜM INDEX'LERİ SİL")
print("=" * 60)
print()

with engine.connect() as conn:
    # Tüm index'leri bul (primary key hariç)
    result = conn.execute(text("""
        SELECT schemaname, tablename, indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND indexname NOT LIKE '%_pkey'
    """))
    
    indexes = list(result)
    print(f"📊 {len(indexes)} index bulundu")
    print()
    
    for schema, table, idx in indexes:
        try:
            conn.execute(text(f"DROP INDEX IF EXISTS {idx} CASCADE"))
            print(f"✅ {idx}")
        except Exception as e:
            print(f"⚠️  {idx}: {str(e)[:50]}")
    
    conn.commit()
    
    # Tüm tabloları sil
    print()
    print("🗑️  Tüm tablolar siliniyor...")
    conn.execute(text("DROP SCHEMA public CASCADE"))
    conn.execute(text("CREATE SCHEMA public"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
    conn.commit()
    print("✅ Schema yeniden oluşturuldu")

print()
print("=" * 60)
print("🎉 FORCE CLEAN TAMAMLANDI!")
print("=" * 60)
print()
print("📝 Şimdi: python direct_railway_setup.py")
