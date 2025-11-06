"""
Veritabanı ve Tabloları Otomatik Oluşturma Script'i
Bu script sistem ilk çalıştırıldığında veritabanını ve tabloları oluşturur.
"""

import pymysql
from sqlalchemy import create_engine, inspect
from app import app, db
from models import *
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def create_database():
    """MySQL veritabanını oluştur"""
    
    # Railway veya production ortamında çalıştırma - veritabanı zaten var
    database_url = os.getenv('DATABASE_URL')
    mysqlhost = os.getenv('MYSQLHOST')
    railway_env = os.getenv('RAILWAY_ENVIRONMENT')
    
    if database_url or mysqlhost or railway_env:
        print("=" * 60)
        print("PRODUCTION/RAILWAY DEPLOYMENT - DATABASE SETUP")
        print("=" * 60)
        print("✅ Production MySQL detected (DATABASE_URL or MYSQLHOST found)")
        print("ℹ️  Database already exists, skipping database creation")
        print("📊 Proceeding to table creation...")
        print()
        return True
    
    # Local development için MySQL'e bağlan ve veritabanı oluştur
    mysql_host = os.getenv('DB_HOST', 'localhost')
    mysql_user = os.getenv('DB_USER', 'root')
    mysql_password = os.getenv('DB_PASSWORD', '')
    mysql_db = os.getenv('DB_NAME', 'minibar_takip')
    
    print("=" * 60)
    print("OTEL MİNİBAR TAKİP SİSTEMİ - VERİTABANI KURULUM")
    print("=" * 60)
    print()
    
    try:
        # MySQL'e bağlan (veritabanı olmadan)
        print(f"📡 MySQL sunucusuna bağlanılıyor... ({mysql_host})")
        connection = pymysql.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        
        # Veritabanını oluştur
        print(f"🗄️  Veritabanı kontrol ediliyor: {mysql_db}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Veritabanı hazır: {mysql_db}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Hatası: {e}")
        print()
        print("🔧 Lütfen kontrol edin:")
        print("   - MySQL servisi çalışıyor mu?")
        print("   - Kullanıcı adı ve şifre doğru mu?")
        print("   - .env dosyası mevcut mu?")
        return False
    except Exception as e:
        print(f"❌ Beklenmeyen Hata: {e}")
        return False

def create_tables():
    """SQLAlchemy tablolarını oluştur"""
    
    print()
    print("📊 Tablolar oluşturuluyor...")
    
    try:
        with app.app_context():
            # Mevcut tabloları kontrol et
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if existing_tables:
                print(f"ℹ️  Mevcut tablolar bulundu: {len(existing_tables)} tablo")
                for table in existing_tables:
                    print(f"   - {table}")
            else:
                print("ℹ️  Henüz tablo yok, yeni tablolar oluşturuluyor...")
            
            # Tüm tabloları oluştur
            db.create_all()
            
            # Oluşturulan tabloları kontrol et
            inspector = inspect(db.engine)
            all_tables = inspector.get_table_names()
            
            print()
            print(f"✅ Toplam {len(all_tables)} tablo hazır:")
            for table in sorted(all_tables):
                print(f"   ✓ {table}")
            
            return True
            
    except Exception as e:
        print(f"❌ Tablo oluşturma hatası: {e}")
        return False

def verify_setup():
    """Kurulumu doğrula"""
    
    print()
    print("🔍 Kurulum doğrulanıyor...")
    
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            
            # Beklenen tablolar (models.py'daki __tablename__ ile eşleşmeli)
            expected_tables = [
                'oteller',
                'kullanicilar',
                'katlar',
                'odalar',
                'urun_gruplari',
                'urunler',
                'stok_hareketleri',
                'personel_zimmet',
                'personel_zimmet_detay',
                'minibar_islemleri',
                'minibar_islem_detay',
                'sistem_ayarlari',
                'sistem_loglari',
                'hata_loglari',
                'audit_logs',
                'otomatik_raporlar',
                'minibar_dolum_talepleri',
                'qr_kod_okutma_loglari'
            ]
            
            existing_tables = inspector.get_table_names()
            missing_tables = [t for t in expected_tables if t not in existing_tables]
            
            if missing_tables:
                print(f"⚠️  Eksik tablolar: {', '.join(missing_tables)}")
                return False
            else:
                print("✅ Tüm tablolar başarıyla oluşturuldu!")
                return True
                
    except Exception as e:
        print(f"❌ Doğrulama hatası: {e}")
        return False

def main():
    """Ana fonksiyon"""
    
    print()
    
    # 1. Veritabanını oluştur
    if not create_database():
        print()
        print("❌ Veritabanı oluşturulamadı. Kurulum iptal edildi.")
        return False
    
    # 2. Tabloları oluştur
    if not create_tables():
        print()
        print("❌ Tablolar oluşturulamadı. Kurulum iptal edildi.")
        return False
    
    # 3. Kurulumu doğrula
    if not verify_setup():
        print()
        print("⚠️  Kurulum tamamlandı ancak bazı tablolar eksik olabilir.")
        return False
    
    # Başarılı
    print()
    print("=" * 60)
    print("🎉 KURULUM BAŞARIYLA TAMAMLANDI!")
    print("=" * 60)
    print()
    print("📝 Sonraki Adımlar:")
    print("   1. Uygulamayı başlatın: python app.py")
    print("   2. Tarayıcıda açın: http://localhost:5014")
    print("   3. İlk kurulum sayfasından sistem yöneticisi oluşturun")
    print()
    print("⚠️  ÖNEMLİ NOT:")
    print("   Eğer mevcut bir veritabanını güncelliyorsanız,")
    print("   QR kod sistemi için migration çalıştırın:")
    print("   python migrations/add_qr_kod_system.py")
    print()
    print("🚀 İyi çalışmalar!")
    print()
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

