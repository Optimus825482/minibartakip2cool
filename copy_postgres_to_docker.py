#!/usr/bin/env python3
"""
Localhost PostgreSQL'den Docker PostgreSQL'e veri kopyalama
"""

import psycopg2
from psycopg2.extras import execute_values

# Kaynak (Localhost PostgreSQL)
source_config = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': '518518Erkan',
    'database': 'minibar_takip'
}

# Hedef (Docker PostgreSQL)
target_config = {
    'host': 'localhost',
    'port': 5433,
    'user': 'minibar_user',
    'password': 'minibar123',
    'database': 'minibar_takip'
}

def get_tables(conn):
    """Tüm tabloları foreign key sırasına göre listele"""
    # Foreign key bağımlılıklarına göre sıralı tablo listesi
    return [
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
        'minibar_dolum_talepleri',
        'qr_kod_okutma_loglari',
        'sistem_ayarlari',
        'sistem_loglari',
        'hata_loglari',
        'audit_logs',
        'otomatik_raporlar'
    ]

def copy_table(source_conn, target_conn, table_name):
    """Bir tabloyu kopyala"""
    print(f"\n📊 Copying table: {table_name}")
    
    # Kaynak tablodan veri çek
    with source_conn.cursor() as src_cur:
        src_cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = src_cur.fetchone()[0]
        print(f"   Source rows: {count}")
        
        if count == 0:
            print(f"   ⚠️  No data to copy")
            return
        
        # Tüm verileri çek
        src_cur.execute(f"SELECT * FROM {table_name}")
        rows = src_cur.fetchall()
        
        # Kolon isimlerini al
        columns = [desc[0] for desc in src_cur.description]
    
    # Hedef tabloya yaz
    with target_conn.cursor() as tgt_cur:
        # Önce tabloyu temizle
        tgt_cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
        
        # Verileri ekle
        if rows:
            cols = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
            
            for row in rows:
                try:
                    tgt_cur.execute(query, row)
                except Exception as e:
                    print(f"   ❌ Error inserting row: {e}")
        
        target_conn.commit()
        print(f"   ✅ Copied: {len(rows)} rows")

def main():
    print("\n" + "="*70)
    print("🚀 PostgreSQL to Docker PostgreSQL Copy Tool")
    print("="*70)
    
    # Bağlantıları aç
    print("\n📍 Connecting to source...")
    source_conn = psycopg2.connect(**source_config)
    
    print("📍 Connecting to target...")
    target_conn = psycopg2.connect(**target_config)
    
    try:
        # Tabloları al
        tables = get_tables(source_conn)
        print(f"\n📋 Found {len(tables)} tables to copy")
        
        # Her tabloyu kopyala
        for table in tables:
            copy_table(source_conn, target_conn, table)
        
        print("\n" + "="*70)
        print("✅ Copy completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        source_conn.close()
        target_conn.close()
        print("\n🔌 Connections closed.")

if __name__ == "__main__":
    main()
