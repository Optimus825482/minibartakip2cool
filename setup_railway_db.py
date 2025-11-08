#!/usr/bin/env python3
"""
Railway PostgreSQL Database Setup
Local'den Railway'e bağlanıp tabloları oluşturur
"""

import psycopg2
from psycopg2 import sql
import sys

# Railway Database URL
DATABASE_URL = "postgresql://postgres:NEOcbkYOOSzROELtJEuVZxdPphGLIXnx@shinkansen.proxy.rlwy.net:36747/railway"

def connect_to_railway():
    """Railway PostgreSQL'e bağlan"""
    try:
        print("🔌 Railway PostgreSQL'e bağlanılıyor...")
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Bağlantı başarılı!")
        return conn
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        sys.exit(1)

def create_tables_with_sqlalchemy():
    """SQLAlchemy ile tabloları oluştur"""
    try:
        print("\n📊 SQLAlchemy ile tablolar oluşturuluyor...")
        
        # Geçici olarak DATABASE_URL'i ayarla
        import os
        os.environ['DATABASE_URL'] = DATABASE_URL
        
        # App ve db'yi import et
        from app import app, db
        
        with app.app_context():
            # Mevcut tabloları kontrol et
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if existing_tables:
                print(f"ℹ️  Mevcut tablolar: {len(existing_tables)}")
                for table in existing_tables:
                    print(f"   - {table}")
                
                print("\n🗑️  Tüm tablolar ve index'ler siliniyor...")
                # Önce tüm index'leri sil
                conn = db.engine.raw_connection()
                cur = conn.cursor()
                cur.execute("""
                    DO $$ DECLARE
                        r RECORD;
                    BEGIN
                        FOR r IN (SELECT indexname FROM pg_indexes WHERE schemaname = 'public') LOOP
                            EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(r.indexname) || ' CASCADE';
                        END LOOP;
                    END $$;
                """)
                conn.commit()
                cur.close()
                conn.close()
                print("✅ Index'ler silindi")
                
                # Sonra tabloları sil
                db.drop_all()
                print("✅ Tablolar silindi")
            
            # Tabloları oluştur
            print("\n🔨 Tablolar oluşturuluyor...")
            try:
                db.create_all()
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print("ℹ️  Bazı index'ler zaten mevcut, devam ediliyor...")
                else:
                    raise
            
            # Kontrol et
            inspector = inspect(db.engine)
            all_tables = inspector.get_table_names()
            
            print(f"\n✅ {len(all_tables)} tablo oluşturuldu:")
            for table in sorted(all_tables):
                print(f"   ✓ {table}")
            
            return True
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_superadmin():
    """Superadmin kullanıcısı oluştur"""
    try:
        print("\n👤 Superadmin oluşturuluyor...")
        
        import os
        os.environ['DATABASE_URL'] = DATABASE_URL
        
        from app import app, db
        from models import Kullanici
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        with app.app_context():
            # Superadmin var mı kontrol et
            existing = Kullanici.query.filter_by(kullanici_adi='superadmin').first()
            
            if existing:
                print("ℹ️  Superadmin zaten mevcut")
                cevap = input("Şifreyi sıfırla? (E/H): ")
                if cevap.upper() == 'E':
                    existing.sifre = generate_password_hash('Admin123!')
                    db.session.commit()
                    print("✅ Şifre sıfırlandı: Admin123!")
                return True
            
            # Yeni superadmin oluştur
            superadmin = Kullanici(
                kullanici_adi='superadmin',
                sifre=generate_password_hash('Admin123!'),
                ad='Super',
                soyad='Admin',
                rol='sistem_yoneticisi',
                aktif=True,
                olusturma_tarihi=datetime.utcnow()
            )
            
            db.session.add(superadmin)
            db.session.commit()
            
            print("✅ Superadmin oluşturuldu!")
            print("\n📝 Giriş Bilgileri:")
            print("   Kullanıcı: superadmin")
            print("   Şifre: Admin123!")
            
            return True
            
    except Exception as e:
        print(f"❌ Superadmin oluşturma hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_connection():
    """Bağlantıyı test et"""
    try:
        conn = connect_to_railway()
        cur = conn.cursor()
        
        # PostgreSQL versiyonu
        cur.execute('SELECT version()')
        version = cur.fetchone()[0]
        print(f"\n📌 PostgreSQL: {version.split(',')[0]}")
        
        # Database bilgileri
        cur.execute('SELECT current_database(), current_user')
        db_name, user = cur.fetchone()
        print(f"📌 Database: {db_name}")
        print(f"📌 User: {user}")
        
        # Tablo sayısı
        cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cur.fetchone()[0]
        print(f"📌 Tablo Sayısı: {table_count}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Doğrulama hatası: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("=" * 60)
    print("RAILWAY POSTGRESQL DATABASE SETUP")
    print("=" * 60)
    
    # 1. Bağlantıyı test et
    if not verify_connection():
        sys.exit(1)
    
    # 2. Tabloları oluştur
    print("\n" + "=" * 60)
    if not create_tables_with_sqlalchemy():
        print("\n❌ Tablolar oluşturulamadı!")
        sys.exit(1)
    
    # 3. Superadmin oluştur
    print("\n" + "=" * 60)
    if not create_superadmin():
        print("\n⚠️  Superadmin oluşturulamadı ama devam edebilirsin")
    
    # 4. Final kontrol
    print("\n" + "=" * 60)
    print("FINAL KONTROL")
    print("=" * 60)
    verify_connection()
    
    print("\n" + "=" * 60)
    print("🎉 KURULUM TAMAMLANDI!")
    print("=" * 60)
    print("\n🌐 Railway URL:")
    print("   https://web-production-243c.up.railway.app")
    print("\n📝 Giriş:")
    print("   Kullanıcı: superadmin")
    print("   Şifre: Admin123!")
    print()

if __name__ == '__main__':
    main()
