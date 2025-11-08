"""
Check if MySQL has data
"""
import pymysql

try:
    # Connect to MySQL
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='minibar_takip',
        port=3306
    )
    
    cursor = conn.cursor()
    
    print("✅ MySQL bağlantısı başarılı!")
    print("\n📊 Tablo kayıt sayıları:\n")
    
    tables = [
        'oteller', 'kullanicilar', 'katlar', 'odalar',
        'urun_gruplari', 'urunler', 'stok_hareketleri',
        'personel_zimmet', 'personel_zimmet_detay',
        'minibar_islemleri', 'minibar_islem_detay'
    ]
    
    total_rows = 0
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_rows += count
            if count > 0:
                print(f"  {table:30} {count:>6} rows")
        except Exception as e:
            print(f"  {table:30} ❌ Error: {str(e)}")
    
    print(f"\n{'='*40}")
    print(f"Toplam kayıt: {total_rows}")
    print(f"{'='*40}")
    
    if total_rows > 0:
        print("\n✅ MySQL'de veri var! Migration yapılabilir.")
    else:
        print("\n⚠️  MySQL'de veri yok!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ MySQL bağlantı hatası: {str(e)}")
    print("\nℹ️  MySQL çalışmıyor olabilir veya database yok")
