#!/usr/bin/env python3
"""
Local PostgreSQL verilerini JSON'a export et
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Local PostgreSQL
local_host = os.getenv('DB_HOST', 'localhost')
local_user = os.getenv('DB_USER', 'minibar_user')
local_password = os.getenv('DB_PASSWORD', 'minibar123')
local_db = os.getenv('DB_NAME', 'minibar_takip')
local_port = os.getenv('DB_PORT', '5433')

local_uri = f'postgresql+psycopg2://{local_user}:{local_password}@{local_host}:{local_port}/{local_db}'
engine = create_engine(local_uri)

Session = sessionmaker(bind=engine)
session = Session()

# Tablo sırası
tables = [
    'oteller', 'kullanicilar', 'kullanici_otel', 'katlar', 'odalar',
    'urun_gruplari', 'urunler', 'stok_hareketleri',
    'personel_zimmet', 'personel_zimmet_detay',
    'minibar_islemleri', 'minibar_islem_detay',
    'minibar_dolum_talepleri', 'misafir_kayitlari', 'dosya_yuklemeleri',
    'qr_kod_okutma_loglari', 'sistem_ayarlari', 'sistem_loglari',
    'hata_loglari', 'audit_logs', 'otomatik_raporlar',
    'ml_metrics', 'ml_models', 'ml_alerts', 'ml_training_logs'
]

print("📤 Local PostgreSQL veriler export ediliyor...")
print()

export_data = {}

for table in tables:
    try:
        result = session.execute(text(f"SELECT * FROM {table}"))
        rows = []
        
        for row in result:
            row_dict = dict(row._mapping)
            
            # Datetime dönüşümü
            for key, value in row_dict.items():
                if isinstance(value, datetime):
                    row_dict[key] = value.isoformat()
            
            rows.append(row_dict)
        
        export_data[table] = rows
        print(f"✅ {table}: {len(rows)} kayıt")
        
    except Exception as e:
        print(f"⚠️  {table}: {str(e)[:50]}")
        export_data[table] = []

# JSON'a kaydet
filename = f"local_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(export_data, f, ensure_ascii=False, indent=2)

print()
print(f"✅ Veriler export edildi: {filename}")
print(f"📊 Toplam: {sum(len(v) for v in export_data.values())} kayıt")

session.close()
