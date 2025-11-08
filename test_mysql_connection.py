#!/usr/bin/env python3
"""MySQL bağlantı testi"""

import pymysql

try:
    # Bağlantı kur
    conn = pymysql.connect(
        host='localhost',
        port=3307,
        user='minibar_user',
        password='minibar123',
        database='minibar_takip'
    )
    
    print('✅ MySQL bağlantısı başarılı!')
    
    cur = conn.cursor()
    
    # Version
    cur.execute('SELECT VERSION()')
    ver = cur.fetchone()[0]
    print(f'MySQL: {ver}')
    
    # Tablo sayısı
    cur.execute('SHOW TABLES')
    tablolar = cur.fetchall()
    print(f'Tablo sayısı: {len(tablolar)}')
    
    # Tabloları listele
    if len(tablolar) > 0:
        print(f'\nMevcut tablolar:')
        for tablo in tablolar:
            tablo_adi = tablo[0]
            cur.execute(f'SELECT COUNT(*) FROM {tablo_adi}')
            row_count = cur.fetchone()[0]
            print(f'  - {tablo_adi}: {row_count} satır')
    
    conn.close()
    print('\n✅ Test tamamlandı!')
    
except Exception as e:
    print(f'❌ Hata: {e}')
    import traceback
    traceback.print_exc()
