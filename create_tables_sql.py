#!/usr/bin/env python3
"""
Railway PostgreSQL - SQL ile tablo oluşturma
"""

import psycopg2
import os

DATABASE_URL = "postgresql://postgres:NEOcbkYOOSzROELtJEuVZxdPphGLIXnx@shinkansen.proxy.rlwy.net:36747/railway"

# Geçici olarak DATABASE_URL'i ayarla
os.environ['DATABASE_URL'] = DATABASE_URL

from app import app, db
from sqlalchemy.schema import CreateTable

def create_tables_with_sql():
    """SQL komutlarıyla tabloları oluştur"""
    try:
        print("🔌 Railway PostgreSQL'e bağlanılıyor...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        print("✅ Bağlantı başarılı!")
        
        print("\n📊 ENUM type'ları oluşturuluyor...")
        
        # ENUM type'ları oluştur
        enums = [
            "CREATE TYPE kullanici_rol AS ENUM ('sistem_yoneticisi', 'admin', 'depo_sorumlusu', 'kat_sorumlusu')",
            "CREATE TYPE rapor_tipi AS ENUM ('gunluk', 'haftalik', 'aylik')",
            "CREATE TYPE audit_islem_tipi AS ENUM ('login', 'logout', 'create', 'update', 'delete', 'view', 'export', 'import', 'backup', 'restore')",
            "CREATE TYPE zimmet_durum AS ENUM ('aktif', 'iade_edildi', 'iptal')",
            "CREATE TYPE hareket_tipi AS ENUM ('giris', 'cikis', 'transfer', 'sayim', 'fire')",
            "CREATE TYPE dolum_talep_durum AS ENUM ('beklemede', 'onaylandi', 'reddedildi', 'tamamlandi')",
            "CREATE TYPE minibar_islem_tipi AS ENUM ('ilk_dolum', 'yeniden_dolum', 'eksik_tamamlama', 'sayim', 'duzeltme')",
            "CREATE TYPE qr_okutma_tipi AS ENUM ('misafir_okutma', 'personel_kontrol', 'sistem_kontrol')"
        ]
        
        for enum_sql in enums:
            try:
                cur.execute(enum_sql)
                enum_name = enum_sql.split()[2]
                print(f"✅ {enum_name} oluşturuldu")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    enum_name = enum_sql.split()[2]
                    print(f"ℹ️  {enum_name} zaten mevcut")
                else:
                    print(f"❌ ENUM hatası: {e}")
        
        print("\n📊 Tablolar oluşturuluyor...")
        
        with app.app_context():
            # Her tablo için CREATE TABLE SQL'i oluştur
            for table in db.metadata.sorted_tables:
                try:
                    create_sql = str(CreateTable(table).compile(db.engine))
                    print(f"\n🔨 {table.name} oluşturuluyor...")
                    cur.execute(create_sql)
                    print(f"✅ {table.name} oluşturuldu")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f"ℹ️  {table.name} zaten mevcut")
                    else:
                        print(f"❌ {table.name} hatası: {e}")
        
        # Kontrol
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cur.fetchone()[0]
        print(f"\n📊 Toplam tablo sayısı: {table_count}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("RAILWAY - SQL İLE TABLO OLUŞTURMA")
    print("=" * 60)
    
    if create_tables_with_sql():
        print("\n✅ Tablolar başarıyla oluşturuldu!")
        print("\nŞimdi superadmin oluştur:")
        print("  python setup_railway_db.py")
    else:
        print("\n❌ Tablolar oluşturulamadı!")
