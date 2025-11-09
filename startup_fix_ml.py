#!/usr/bin/env python3
"""
Startup ML Fix - Railway deployment sonrası otomatik çalışır
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

def fix_ml_metrics_on_startup():
    """Startup'ta ML Metrics tablosunu kontrol et ve düzelt"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("⚠️  DATABASE_URL yok, fix atlanıyor")
            return True
        
        # PostgreSQL URL fix
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        
        print("🔧 ML Metrics tablosu kontrol ediliyor...")
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        if 'ml_metrics' not in inspector.get_table_names():
            print("⚠️  ml_metrics tablosu yok, fix atlanıyor")
            return True
        
        columns = [col['name'] for col in inspector.get_columns('ml_metrics')]
        
        if 'entity_type' not in columns:
            print("✅ entity_type kolonu zaten yok")
            return True
        
        print("🔧 entity_type kolonu kaldırılıyor...")
        
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE ml_metrics DROP COLUMN IF EXISTS entity_type CASCADE;"))
            conn.execute(text("DROP INDEX IF EXISTS idx_ml_metrics_entity;"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ml_metrics_entity ON ml_metrics(entity_id);"))
            conn.commit()
        
        print("✅ ML Metrics tablosu düzeltildi!")
        return True
        
    except Exception as e:
        print(f"⚠️  ML Metrics fix hatası (devam ediliyor): {str(e)}")
        return True  # Hata olsa bile uygulama başlasın

if __name__ == '__main__':
    fix_ml_metrics_on_startup()
