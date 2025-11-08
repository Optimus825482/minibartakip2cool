#!/usr/bin/env python3
"""
Railway PostgreSQL Database Temizleme
Tüm tabloları ve index'leri siler
"""

import psycopg2

DATABASE_URL = "postgresql://postgres:NEOcbkYOOSzROELtJEuVZxdPphGLIXnx@shinkansen.proxy.rlwy.net:36747/railway"

def clean_database():
    """Tüm tabloları ve index'leri sil"""
    try:
        print("🔌 Railway PostgreSQL'e bağlanılıyor...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("✅ Bağlantı başarılı!")
        
        # Tüm tabloları sil
        print("\n🗑️  Tablolar siliniyor...")
        cur.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    RAISE NOTICE 'Dropped table: %', r.tablename;
                END LOOP;
            END $$;
        """)
        print("✅ Tablolar silindi")
        
        # ENUM type'ları sil
        print("\n🗑️  ENUM type'ları siliniyor...")
        cur.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT typname FROM pg_type WHERE typtype = 'e') LOOP
                    EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE';
                    RAISE NOTICE 'Dropped type: %', r.typname;
                END LOOP;
            END $$;
        """)
        print("✅ ENUM type'ları silindi")
        
        # Kontrol
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cur.fetchone()[0]
        
        print(f"\n📊 Kalan tablo sayısı: {table_count}")
        
        cur.close()
        conn.close()
        
        print("\n✅ Database temizlendi!")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("RAILWAY DATABASE TEMIZLEME")
    print("=" * 60)
    print("\n⚠️  TÜM TABLOLAR VE INDEX'LER SİLİNECEK!")
    cevap = input("Devam etmek istiyor musun? (E/H): ")
    
    if cevap.upper() == 'E':
        clean_database()
    else:
        print("❌ İşlem iptal edildi")
