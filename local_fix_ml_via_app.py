#!/usr/bin/env python3
"""
Local ML Metrics Tablosu Düzeltme (Flask App Context ile)
"""

from app import app, db
from sqlalchemy import text, inspect

def fix_ml_metrics():
    """ml_metrics tablosundan entity_type kolonunu kaldır"""
    with app.app_context():
        try:
            print("🔍 ml_metrics tablosu kontrol ediliyor...")
            
            # Tablo var mı kontrol et
            inspector = inspect(db.engine)
            
            if 'ml_metrics' not in inspector.get_table_names():
                print("⚠️ ml_metrics tablosu bulunamadı!")
                print("🔧 Tablo oluşturuluyor...")
                db.create_all()
                print("✅ Tablo oluşturuldu!")
                return True
            
            # Kolonları kontrol et
            columns = [col['name'] for col in inspector.get_columns('ml_metrics')]
            print(f"📋 Mevcut kolonlar: {columns}")
            
            if 'entity_type' not in columns:
                print("✅ entity_type kolonu zaten yok. Tablo güncel!")
                return True
            
            print("🔧 entity_type kolonu kaldırılıyor...")
            
            # entity_type kolonunu kaldır
            with db.engine.connect() as conn:
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
    print("LOCAL ML METRICS FIX (via Flask App)")
    print("=" * 60)
    
    success = fix_ml_metrics()
    
    if success:
        print("\n✅ İşlem başarıyla tamamlandı!")
        print("🚀 Artık local'de ML sistemi çalışacak!")
    else:
        print("\n❌ İşlem başarısız!")
