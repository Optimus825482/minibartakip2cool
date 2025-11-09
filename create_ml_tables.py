"""
ML Tabloları Oluşturma Scripti
Docker PostgreSQL'e bağlanır ve ML tablolarını oluşturur
"""

import sys
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

print("=" * 60)
print("🤖 ML ANOMALI TESPİT SİSTEMİ - TABLO OLUŞTURMA")
print("=" * 60)
print()

# Veritabanı bilgilerini göster
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'minibar_takip')
db_port = os.getenv('DB_PORT', '5432')
db_user = os.getenv('DB_USER', 'minibar_user')

print(f"📊 Veritabanı Bilgileri:")
print(f"   Host: {db_host}")
print(f"   Port: {db_port}")
print(f"   Database: {db_name}")
print(f"   User: {db_user}")
print()

# Flask app'i import et
try:
    from app import app, db
    from models import MLMetric, MLModel, MLAlert, MLTrainingLog
    
    print("✅ Modüller yüklendi")
    print()
    
    with app.app_context():
        # Mevcut tabloları kontrol et
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print("📋 Mevcut Tablolar:")
        for table in sorted(existing_tables):
            print(f"   - {table}")
        print()
        
        # ML tablolarını kontrol et
        ml_tables = ['ml_metrics', 'ml_models', 'ml_alerts', 'ml_training_logs']
        missing_tables = [t for t in ml_tables if t not in existing_tables]
        
        if not missing_tables:
            print("✅ Tüm ML tabloları zaten mevcut!")
            print()
            
            # Kayıt sayılarını göster
            print("📊 Tablo İstatistikleri:")
            try:
                print(f"   - ml_metrics: {db.session.query(MLMetric).count()} kayıt")
                print(f"   - ml_models: {db.session.query(MLModel).count()} kayıt")
                print(f"   - ml_alerts: {db.session.query(MLAlert).count()} kayıt")
                print(f"   - ml_training_logs: {db.session.query(MLTrainingLog).count()} kayıt")
            except Exception as e:
                print(f"   ⚠️  İstatistik alınamadı: {str(e)}")
            
            sys.exit(0)
        
        print(f"⚠️  Eksik ML Tabloları: {', '.join(missing_tables)}")
        print()
        
        # Tabloları oluştur
        print("🚀 ML tabloları oluşturuluyor...")
        
        try:
            # Sadece ML tablolarını oluştur
            db.create_all()
            
            print("✅ ML tabloları başarıyla oluşturuldu!")
            print()
            
            # Yeni tabloları kontrol et
            inspector = inspect(db.engine)
            new_tables = inspector.get_table_names()
            
            print("📋 Oluşturulan Tablolar:")
            for table in ml_tables:
                if table in new_tables:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} (oluşturulamadı)")
            print()
            
            # Index'leri kontrol et
            print("📋 Index'ler:")
            for table in ml_tables:
                if table in new_tables:
                    indexes = inspector.get_indexes(table)
                    if indexes:
                        print(f"   {table}:")
                        for idx in indexes:
                            print(f"      - {idx['name']}")
                    else:
                        print(f"   {table}: Index yok")
            print()
            
            print("=" * 60)
            print("✅ İŞLEM TAMAMLANDI!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ HATA: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            sys.exit(1)

except Exception as e:
    print(f"❌ Modül yükleme hatası: {str(e)}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
