#!/usr/bin/env python3
"""
Railway'deki tüm index'leri temizle
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv('.env.railway')

railway_url = os.getenv('RAILWAY_DATABASE_URL')
if railway_url:
    railway_url = railway_url.replace('postgresql://', 'postgresql+psycopg2://')

engine = create_engine(railway_url)

print("🧹 Index'ler temizleniyor...")

with engine.connect() as conn:
    # Tüm index'leri bul
    result = conn.execute(text("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND indexname NOT LIKE 'pg_%'
        AND indexname NOT LIKE '%_pkey'
    """))
    
    indexes = [row[0] for row in result]
    
    print(f"📊 {len(indexes)} index bulundu")
    
    for idx in indexes:
        try:
            conn.execute(text(f"DROP INDEX IF EXISTS {idx} CASCADE"))
            print(f"✅ {idx}")
        except Exception as e:
            print(f"⚠️  {idx}: {str(e)[:50]}")
    
    conn.commit()

print("\n✅ Index temizleme tamamlandı!")
print("📝 Şimdi: python direct_railway_setup.py")
