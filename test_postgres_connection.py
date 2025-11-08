#!/usr/bin/env python3
"""PostgreSQL bağlantı testi"""

import psycopg2

try:
    # Bağlantı kur
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='518518Erkan',
        database='minibar_takip'
    )
    
    print('✅ PostgreSQL bağlantısı başarılı!')
    
    cur = conn.cursor()
    
    # Version
    cur.execute('SELECT version()')
    ver = cur.fetchone()[0]
    print(f'PostgreSQL: {ver[:60]}...')
    
    # Tablo sayısı
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    tablo_sayisi = cur.fetchone()[0]
    print(f'Tablo sayısı: {tablo_sayisi}')
    
    # Tabloları listele
    if tablo_sayisi > 0:
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
        tablolar = cur.fetchall()
        print(f'\nMevcut tablolar:')
        for tablo in tablolar:
            cur.execute(f"SELECT COUNT(*) FROM {tablo[0]}")
            row_count = cur.fetchone()[0]
            print(f'  - {tablo[0]}: {row_count} satır')
    
    conn.close()
    print('\n✅ Test tamamlandı!')
    
except Exception as e:
    print(f'❌ Hata: {e}')
    import traceback
    traceback.print_exc()
