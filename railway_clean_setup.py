#!/usr/bin/env python3
"""
Railway PostgreSQL Clean Setup
Tüm tabloları ve index'leri temizleyip yeniden oluşturur
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load .env.railway file
load_dotenv('.env.railway')

def get_railway_connection():
    """Railway PostgreSQL connection string"""
    database_url = os.getenv('RAILWAY_DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        return database_url
    
    pg_host = os.getenv('RAILWAY_PGHOST')
    pg_user = os.getenv('RAILWAY_PGUSER')
    pg_password = os.getenv('RAILWAY_PGPASSWORD')
    pg_db = os.getenv('RAILWAY_PGDATABASE')
    pg_port = os.getenv('RAILWAY_PGPORT', '5432')
    
    return f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'

def clean_database():
    """Tüm tabloları ve index'leri temizle"""
    
    print("=" * 60)
    print("🧹 RAILWAY DATABASE CLEAN SETUP")
    print("=" * 60)
    print()
    
    try:
        connection_uri = get_railway_connection()
        print("📡 Railway PostgreSQL'e bağlanılıyor...")
        
        engine = create_engine(connection_uri, echo=False)
        
        with engine.connect() as conn:
            # PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Bağlantı başarılı!")
            print(f"📊 {version.split(',')[0]}")
            print()
            
            # Tüm tabloları CASCADE ile sil
            print("🗑️  Tüm tablolar siliniyor (CASCADE)...")
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.commit()
            print("✅ Schema silindi")
            
            # Schema'yı yeniden oluştur
            print("🔨 Schema yeniden oluşturuluyor...")
            conn.execute(text("CREATE SCHEMA public"))
            conn.commit()
            print("✅ Schema oluşturuldu")
            
            # Permissions
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            conn.commit()
            print("✅ Permissions ayarlandı")
            
            # Alembic version tablosunu da temizle
            try:
                conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
                conn.commit()
                print("✅ Alembic version temizlendi")
            except:
                pass
        
        print()
        print("=" * 60)
        print("🎉 DATABASE TEMİZLENDİ!")
        print("=" * 60)
        print()
        print("📝 Sonraki adım:")
        print("   python railway_setup.py (tabloları oluştur)")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = clean_database()
    sys.exit(0 if success else 1)
