#!/usr/bin/env python3
"""
MySQL'e örnek veri yükler (Migration testi için)
"""

import pymysql
from datetime import datetime, timedelta
import random


def create_connection():
    """MySQL bağlantısı oluştur"""
    return pymysql.connect(
        host='localhost',
        port=3307,
        user='minibar_user',
        password='minibar123',
        database='minibar_takip',
        charset='utf8mb4'
    )


def create_tables(conn):
    """Tabloları oluştur"""
    cursor = conn.cursor()
    
    # Oteller tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS oteller (
            id INT AUTO_INCREMENT PRIMARY KEY,
            otel_adi VARCHAR(200) NOT NULL,
            adres TEXT,
            telefon VARCHAR(20),
            email VARCHAR(100),
            aktif BOOLEAN DEFAULT TRUE,
            olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
            guncelleme_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Kullanıcılar tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            otel_id INT NOT NULL,
            kullanici_adi VARCHAR(50) UNIQUE NOT NULL,
            sifre VARCHAR(255) NOT NULL,
            ad_soyad VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            telefon VARCHAR(20),
            rol ENUM('admin', 'yonetici', 'personel') DEFAULT 'personel',
            aktif BOOLEAN DEFAULT TRUE,
            son_giris DATETIME,
            olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (otel_id) REFERENCES oteller(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Katlar tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS katlar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            otel_id INT NOT NULL,
            kat_adi VARCHAR(50) NOT NULL,
            kat_no INT NOT NULL,
            aktif BOOLEAN DEFAULT TRUE,
            olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (otel_id) REFERENCES oteller(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Odalar tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS odalar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            kat_id INT NOT NULL,
            oda_no VARCHAR(20) NOT NULL,
            oda_tipi VARCHAR(50),
            durum ENUM('bos', 'dolu', 'temizlik', 'bakim') DEFAULT 'bos',
            qr_kod VARCHAR(100) UNIQUE,
            aktif BOOLEAN DEFAULT TRUE,
            olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kat_id) REFERENCES katlar(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Ürün Grupları tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urun_gruplari (
            id INT AUTO_INCREMENT PRIMARY KEY,
            otel_id INT NOT NULL,
            grup_adi VARCHAR(100) NOT NULL,
            aciklama TEXT,
            aktif BOOLEAN DEFAULT TRUE,
            olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (otel_id) REFERENCES oteller(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Ürünler tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urunler (
            id INT AUTO_INCREMENT PRIMARY KEY,
            otel_id INT NOT NULL,
            grup_id INT,
            urun_adi VARCHAR(200) NOT NULL,
            barkod VARCHAR(50) UNIQUE,
            birim VARCHAR(20),
            fiyat DECIMAL(10,2),
            kritik_stok_seviyesi INT DEFAULT 10,
            aktif BOOLEAN DEFAULT TRUE,
            olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (otel_id) REFERENCES oteller(id) ON DELETE CASCADE,
            FOREIGN KEY (grup_id) REFERENCES urun_gruplari(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Stok Hareketleri tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stok_hareketleri (
            id INT AUTO_INCREMENT PRIMARY KEY,
            urun_id INT NOT NULL,
            hareket_tipi ENUM('giris', 'cikis', 'sayim', 'fire') NOT NULL,
            miktar INT NOT NULL,
            onceki_stok INT,
            yeni_stok INT,
            aciklama TEXT,
            kullanici_id INT,
            islem_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (urun_id) REFERENCES urunler(id) ON DELETE CASCADE,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    conn.commit()
    print("✅ Tablolar oluşturuldu")


def insert_sample_data(conn):
    """Örnek veri ekle"""
    cursor = conn.cursor()
    
    # Otel ekle
    cursor.execute("""
        INSERT INTO oteller (otel_adi, adres, telefon, email) VALUES
        ('Grand Hotel Istanbul', 'Taksim, Istanbul', '+90 212 123 4567', 'info@grandhotel.com'),
        ('Seaside Resort Antalya', 'Lara, Antalya', '+90 242 987 6543', 'info@seasideresort.com')
    """)
    
    # Kullanıcılar ekle
    cursor.execute("""
        INSERT INTO kullanicilar (otel_id, kullanici_adi, sifre, ad_soyad, email, rol) VALUES
        (1, 'admin', 'pbkdf2:sha256:600000$abc123', 'Admin User', 'admin@hotel.com', 'admin'),
        (1, 'yonetici1', 'pbkdf2:sha256:600000$def456', 'Ahmet Yılmaz', 'ahmet@hotel.com', 'yonetici'),
        (1, 'personel1', 'pbkdf2:sha256:600000$ghi789', 'Ayşe Demir', 'ayse@hotel.com', 'personel'),
        (2, 'admin2', 'pbkdf2:sha256:600000$jkl012', 'Mehmet Kaya', 'mehmet@resort.com', 'admin')
    """)
    
    # Katlar ekle
    cursor.execute("""
        INSERT INTO katlar (otel_id, kat_adi, kat_no) VALUES
        (1, 'Zemin Kat', 0),
        (1, '1. Kat', 1),
        (1, '2. Kat', 2),
        (2, 'Zemin Kat', 0),
        (2, '1. Kat', 1)
    """)
    
    # Odalar ekle
    rooms = []
    for floor_id in range(1, 6):
        for room_num in range(1, 11):
            room_no = f"{floor_id}0{room_num}"
            qr_code = f"QR-{room_no}-{random.randint(1000, 9999)}"
            rooms.append((floor_id, room_no, 'Standart', 'bos', qr_code))
    
    cursor.executemany("""
        INSERT INTO odalar (kat_id, oda_no, oda_tipi, durum, qr_kod) 
        VALUES (%s, %s, %s, %s, %s)
    """, rooms)
    
    # Ürün Grupları ekle
    cursor.execute("""
        INSERT INTO urun_gruplari (otel_id, grup_adi, aciklama) VALUES
        (1, 'İçecekler', 'Soğuk ve sıcak içecekler'),
        (1, 'Atıştırmalıklar', 'Cips, çikolata vb.'),
        (1, 'Alkollü İçecekler', 'Bira, şarap, viski'),
        (2, 'İçecekler', 'Soğuk ve sıcak içecekler')
    """)
    
    # Ürünler ekle
    products = [
        (1, 1, 'Coca Cola 330ml', 'CC330', 'Adet', 15.00),
        (1, 1, 'Fanta 330ml', 'FN330', 'Adet', 15.00),
        (1, 1, 'Su 500ml', 'SU500', 'Adet', 5.00),
        (1, 1, 'Ayran 250ml', 'AY250', 'Adet', 8.00),
        (1, 2, 'Çikolata', 'CK001', 'Adet', 12.00),
        (1, 2, 'Cips', 'CP001', 'Adet', 10.00),
        (1, 3, 'Efes Pilsen 500ml', 'EF500', 'Adet', 35.00),
        (1, 3, 'Şarap Kırmızı', 'SR001', 'Şişe', 150.00),
        (2, 4, 'Coca Cola 330ml', 'CC330-2', 'Adet', 15.00),
        (2, 4, 'Su 500ml', 'SU500-2', 'Adet', 5.00)
    ]
    
    cursor.executemany("""
        INSERT INTO urunler (otel_id, grup_id, urun_adi, barkod, birim, fiyat) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, products)
    
    # Stok Hareketleri ekle
    stock_movements = []
    for product_id in range(1, 11):
        # İlk stok girişi
        miktar = random.randint(50, 200)
        stock_movements.append((
            product_id, 'giris', miktar, 0, miktar, 
            'İlk stok girişi', 1, datetime.now() - timedelta(days=30)
        ))
        
        # Birkaç çıkış hareketi
        current_stock = miktar
        for _ in range(random.randint(3, 8)):
            cikis = random.randint(5, 20)
            if current_stock >= cikis:
                onceki = current_stock
                current_stock -= cikis
                stock_movements.append((
                    product_id, 'cikis', cikis, onceki, current_stock,
                    'Minibar tüketimi', random.randint(1, 4),
                    datetime.now() - timedelta(days=random.randint(1, 29))
                ))
    
    cursor.executemany("""
        INSERT INTO stok_hareketleri 
        (urun_id, hareket_tipi, miktar, onceki_stok, yeni_stok, aciklama, kullanici_id, islem_tarihi) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, stock_movements)
    
    conn.commit()
    print("✅ Örnek veriler eklendi")


def show_summary(conn):
    """Veri özetini göster"""
    cursor = conn.cursor()
    
    tables = [
        'oteller', 'kullanicilar', 'katlar', 'odalar',
        'urun_gruplari', 'urunler', 'stok_hareketleri'
    ]
    
    print("\n📊 MySQL Veri Özeti:")
    print("="*50)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:25} : {count:5} rows")
    
    print("="*50)


def main():
    """Ana fonksiyon"""
    print("\n🚀 MySQL Örnek Veri Yükleme")
    print("="*50)
    
    try:
        conn = create_connection()
        print("✅ MySQL bağlantısı başarılı")
        
        create_tables(conn)
        insert_sample_data(conn)
        show_summary(conn)
        
        conn.close()
        print("\n✅ İşlem tamamlandı!")
        print("\n💡 Şimdi migration script'ini çalıştırabilirsin:")
        print("   python run_migration.py")
        
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
