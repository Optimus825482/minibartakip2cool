#!/usr/bin/env python3
"""
Local ML Metrics Tablosu Düzeltme
entity_type kolonunu kaldır (Railway'deki gibi)
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

def fix_local_ml_metrics():
    """Local database'deki ml_metrics tablosunu düzelt"""
    try:
        # Local database URI
        db_uri = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/minibar_db')
        
        print("🔍 Database bağlantısı kuruluyor...")
        print(f"📍 URI: {db_uri[:50]}...")
        
        engine = create_engine(db_uri)
        
        # Tablo var mı kontrol et
        inspector = inspect(engine)
        if 'ml_metrics' not in inspector.get_table_names():
            print("⚠️ ml_metrics tablosu bulunamadı. Tablo oluşturulacak...")
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ml_metrics (
                        id SERIAL PRIMARY KEY,
                        metric_type VARCHAR(50) NOT NULL,
                        entity_id INTEGER NOT NULL,
                        metric_value DOUBLE PRECISION NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        extra_data JSONB
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_ml_metrics_type_time ON ml_metrics(metric_type, timestamp);
                    CREATE INDEX IF NOT EXISTS idx_ml_metrics_entity ON ml_metrics(entity_id);
                """))
                conn.commit()
                print("✅ ml_metrics tablosu oluşturuldu!")
            return True
        
        # Kolonları kontrol et
        columns = [col['name'] for col in inspector.get_columns('ml_metrics')]
        print(f"📋 Mevcut kolonlar: {columns}")
        
        if 'entity_type' not in columns:
            print("✅ entity_type kolonu zaten yok. Tablo güncel!")
            return True
        
        print("🔧 entity_type kolonu kaldırılıyor...")
        
        with engine.connect() as conn:
            # entity_type kolonunu kaldır
            conn.execute(text("""
                ALTER TABLE ml_metrics 
                DROP COLUMN IF EXISTS entity_type CASCADE;
            """))
            conn.commit()
            
            print("✅ entity_type kolonu başarıyla kaldırıldı!")
        
        # Kontrol
        columns_after = [col['name'] for col in inspector.get_columns('ml_metrics')]
        print(f"📋 Güncel kolonlar: {columns_after}")
        
        return True
        
    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("LOCAL ML METRICS FIX")
    print("=" * 60)
    
    success = fix_local_ml_metrics()
    
    if success:
        print("\n✅ İşlem başarıyla tamamlandı!")
        print("🚀 Artık local'de ML sistemi çalışacak!")
        sys.exit(0)
    else:
        print("\n❌ İşlem başarısız!")
        sys.exit(1)
